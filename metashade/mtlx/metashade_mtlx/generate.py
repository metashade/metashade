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

import argparse
import os
from pathlib import Path
import shutil
import sys
import abc

import MaterialX as mx
from metashade.glsl import frag
from metashade._rtsl.qualifiers import Direction

from metashade_mtlx import dtypes

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
        nodedef_name: str = None
    ):
        """
        Add a node implementation.
        
        Args:
            func_name: Name of the generated function
            mx_doc_string: Documentation string
            nodedef_name: If provided, reference this existing MaterialX nodedef
                          instead of creating a new one. Used for overrides.
        """
        # Get the function from the generator to access reflection data
        func = getattr(self._sh, func_name)
        if nodedef_name is None:
            nodedef_name = f'ND_{func_name}'
   
        if self._nodedef_doc is not None:
            # Create new nodedef
            nodedef = self._nodedef_doc.addNodeDef(
                name=nodedef_name,
                node=func_name,
                type=''  # Empty type means no auto-created output
            )
            nodedef.setDocString(mx_doc_string)

            # Add parameters in their original order
            for param_name, param_def in func._param_defs.items():
                is_output = any(
                    qualifier.direction == Direction.OUT 
                    for qualifier in param_def.qualifiers
                )
                param_type = dtypes.metashade_to_mtlx(param_def.dtype_factory)
                
                if is_output:
                    output_param = nodedef.addOutput(param_name, param_type)
                    output_param.setDocString(f'Output parameter {param_name}')
                else:
                    input_param = nodedef.addInput(param_name, param_type)
                    input_param.setDocString(f'Input parameter {param_name}')

            # Impl name for new nodes
            impl_name = f'IM_{func_name}_{self._mx_target_name}'
        else:
            nodedef = None
            # Override: replace mx_ prefix with IM_
            impl_name = f'IM_{func_name.removeprefix("mx_")}_{self._mx_target_name}'

        # Create implementation
        impl = self._impl_doc.addImplementation(impl_name)
        if nodedef is None:
            impl.setNodeDefString(nodedef_name)  # Reference existing by name
        else:
            impl.setNodeDef(nodedef)
  # Reference newly created nodedef
        impl.setTarget(self._mx_target_name)
        impl.setFile(self._src_file_name)
        impl.setFunction(func_name)
        impl.setDocString(mx_doc_string)

class GlslGeneratorContext(GeneratorContext):
    @property
    def _src_extension(self):
        return 'glsl'
    
    @property
    def _mx_target_name(self):
        return 'genglsl'

    def _create_generator(self):
        return frag.Generator(self._src_file, glsl_version = '')
