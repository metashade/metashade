# Copyright 2025 Pavlo Penenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import sys
import abc
from collections.abc import Callable

import MaterialX as mx
from metashade.targets.glsl import frag
from metashade.targets._clike.context import Function, Out, InOut

from metashade.mtlx import dtypes

# MaterialX stdlib conventions for inputs bound to geometric properties.
_DEFAULT_GEOMPROPS = {
    'texcoord': 'UV0',
    'position': 'Pobject',
}

class GeneratorContext:
    def __init__(self, base_name, out_dir, impl_only: bool = False):
        """
        Initialize generator context.
        
        Args:
            base_name: Base name for output files (e.g., 'metashade_pbrlib')
            out_dir: Output directory path
            impl_only: If True, only generate impl file (skip nodedef)
                       for overriding existing MaterialX nodes
        """
        base_impl_name = f'{base_name}_{self._mx_target_name}_impl'

        self._src_file_name = f'{base_impl_name}.{self._src_extension}'
        self._src_path = out_dir / self._src_file_name

        self._nodedef_doc_path = None if impl_only else out_dir / f'{base_name}_defs.mtlx'
        self._impl_doc_path = out_dir / f'{base_impl_name}.mtlx'

    def __enter__(self):
        self._nodedef_doc = None if self._nodedef_doc_path is None else mx.createDocument()
        self._impl_doc = mx.createDocument()
        self._src_file = open(self._src_path, 'w')
        self._sh = self._create_generator()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self._src_file.close()
        
        if exc_type is not None:
            print(
                f"Error during generation: {exc_type.__name__}: {exc_value}",
                file=sys.stderr
            )
            return False
        
        # Only write nodedef doc if it exists
        if self._nodedef_doc is not None:
            mx.writeToXmlFile(self._nodedef_doc, str(self._nodedef_doc_path))
        mx.writeToXmlFile(self._impl_doc, str(self._impl_doc_path))

        print(f"Generated files:")
        if self._nodedef_doc_path is not None:
            print(f"  - {self._nodedef_doc_path}")
        print(f"  - {self._impl_doc_path}")
        print(f"  - {self._src_path}")
        return True
    
    @abc.abstractmethod
    def _create_generator(self):
        pass

    @property
    @abc.abstractmethod 
    def _src_extension(self):
        pass

    @property
    @abc.abstractmethod
    def _mx_target_name(self):
        pass

    def add_node_impl(
        self,
        func_name: str,
        mx_doc_string: str,
        nodedef_name: str = None,
        input_metadata: dict | None = None,
    ) -> mx.NodeDef | None:
        """
        Add a node implementation.
        
        Args:
            func_name: Name of the generated function
            mx_doc_string: Documentation string
            nodedef_name: If provided, reference this existing MaterialX nodedef
                          instead of creating a new one. Used for overrides.
            input_metadata: Mapping of parameter names to
                            ``InputMetadata``.  The ``.doc`` field overrides
                            the generic ``"Input parameter {name}"`` default.

        Returns:
            The new nodedef, or ``None`` if *nodedef_name* references an
            existing one or this context is ``impl_only``.
        """
        # Get the function from the generator to access reflection data
        func = getattr(self._sh, func_name)
        node_category = func_name.removeprefix("mx_")
        if nodedef_name is None:
            nodedef_name = f'ND_{node_category}'

        if self._nodedef_doc is not None:
            # Create new nodedef
            nodedef = self._nodedef_doc.addNodeDef(
                name=nodedef_name,
                node=node_category,
                type=''  # Empty type means no auto-created output
            )
            nodedef.setDocString(mx_doc_string)

            # Add parameters in their original order, skipping codegen-injected
            # params (closureData) that don't belong in the nodedef schema.
            _CODEGEN_PARAMS = {'closureData'}
            for param_name, param in func._param_defs.items():
                if param_name in _CODEGEN_PARAMS:
                    continue

                is_output = isinstance(param, (Out, InOut))
                param_type = dtypes.metashade_to_mtlx(param.dtype_factory)

                if is_output:
                    output_param = nodedef.addOutput(param_name, param_type)
                    output_param.setDocString(f'Output parameter {param_name}')
                else:
                    input_param = nodedef.addInput(param_name, param_type)
                    metadata = (input_metadata or {}).get(param_name)
                    doc = metadata.doc if metadata is not None else None
                    if not doc:
                        doc = f'Input parameter {param_name}'
                    input_param.setDocString(doc)

        else:
            nodedef = None

        impl_name = f'IM_{node_category}_{self._mx_target_name}'

        # Create implementation
        impl = self._impl_doc.addImplementation(impl_name)
        if nodedef is None:
            impl.setNodeDefString(nodedef_name)  # Reference existing by name
        else:
            impl.setNodeDef(nodedef)  # Reference newly created nodedef
        impl.setTarget(self._mx_target_name)
        impl.setFile(self._src_file_name)
        impl.setFunction(func_name)
        impl.setDocString(mx_doc_string)
        return nodedef

    def add_std_node_impl(self, py_func: Callable, nodegroup: str) -> None:
        """Add a node implemented by a ``metashade.std`` function.

        Instantiates *py_func* and calls :meth:`add_function_node_impl`.

        Args:
            py_func: A function exported with ``@metashade.modules.export``
            nodegroup: MaterialX nodegroup, e.g. ``procedural2d``
        """
        self._sh.instantiate(py_func)
        self.add_function_node_impl(
            getattr(self._sh, py_func.__name__), nodegroup
        )

    def add_function_node_impl(self, func: Function, nodegroup: str) -> None:
        """Add a node implemented by a Metashade function.

        MaterialX source-code nodes return their results through output
        parameters, so this generates a wrapper that assigns the return
        value of *func* to the output ``out``.  The node category is the
        function name, and the nodedef takes its doc and input defaults
        from the function's reflection data.

        Args:
            func: A function defined in this context's generator, with
                  either ``sh.function()`` or ``sh.instantiate()``
            nodegroup: MaterialX nodegroup, e.g. ``procedural2d``
        """
        sh = self._sh
        node_category = func._name
        param_defs = func._param_defs
        return_type = func._return_dtype_factory
        mtlx_type = dtypes.metashade_to_mtlx(return_type)
        func_name = f'mx_{node_category}_{mtlx_type}'

        with sh.function(func_name)(**param_defs, out_=sh.Out(return_type)):
            sh.out_ = func(
                **{name: getattr(sh, name) for name in param_defs}
            )

        # TODO: parameter docs, see
        # https://github.com/metashade/metashade/issues/274
        summary = (func._doc or '').strip().split('\n')[0]
        nodedef = self.add_node_impl(
            func_name=func_name,
            mx_doc_string=summary,
            nodedef_name=f'ND_{node_category}_{mtlx_type}',
        )
        if nodedef is None:
            return

        nodedef.setNodeString(node_category)
        nodedef.setNodeGroup(nodegroup)
        for name, param in param_defs.items():
            mx_input = nodedef.getInput(name)
            if param.default is not None:
                mx_input.setValueString(str(param.default))
            geomprop = _DEFAULT_GEOMPROPS.get(name)
            if geomprop is not None:
                mx_input.setDefaultGeomPropString(geomprop)

        # MaterialX binds source-code outputs by position, so the nodedef can
        # use the conventional name even though ``out`` is a GLSL keyword.
        mx_output = nodedef.getOutput('out_')
        mx_output.setName('out')
        mx_output.setDocString(summary)

class GlslGeneratorContext(GeneratorContext):
    @property
    def _src_extension(self):
        return 'glsl'
    
    @property
    def _mx_target_name(self):
        return 'genglsl'

    def _create_generator(self):
        return frag.Generator(self._src_file, glsl_version = '')
