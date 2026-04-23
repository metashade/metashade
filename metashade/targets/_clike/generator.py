# Copyright 2017 Pavlo Penenko
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

import inspect
import types
import re
import metashade.targets._base.generator as base
from . import arrays, context, struct

class Generator(base.Generator):
    def function(self, name : str, return_type = None):
        return context.FunctionDecl(self, name, return_type)

    def struct(self, name, emit=True):
        return struct.StructDef(self, name, emit=emit)
    
    def array(self, element_type, dims):
        element_type = element_type._get_dtype()
        array_class_name = f"Array_{element_type.__name__}_{dims}"
        array_class = getattr(self, array_class_name, None)
        if array_class is None:
            array_class = type(
                array_class_name,
                (arrays.ArrayBase,),
                {
                    "_sh": self,
                    "_element_type": element_type,
                    "_dims": dims
                }
            )
            self._set_global(array_class_name, array_class)
        return array_class

    def include(self, file_path : str):
        self._emit(f'#include "{file_path}"\n')

    def if_(self, condition):
        return context.If(self, condition)
    
    def else_(self):
        return context.Else(self)
    
    def _single_line_comment(self, comment):
        self._emit_indent()
        self._emit(f'// {comment}\n')

    def _resolve_annotation(self, annotation: str):
        match = re.match(r'^(Out|InOut)\[(.+)\]$', annotation)
        if match:
            qualifier_str, inner_type_name = match.groups()
            inner_type = getattr(self, inner_type_name)
            if qualifier_str == 'Out':
                return context.Out(inner_type)
            else:
                return context.InOut(inner_type)

        return getattr(self, annotation)

    def _resolve_param(self, param: inspect.Parameter):
        """Resolve a function parameter to a Param instance."""
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            raise ValueError(f"Parameter '{param.name}' has no type annotation")
        
        # Resolve the dtype from string annotation
        resolved = self._resolve_annotation(annotation)
        
        # Check if there's a default value
        if param.default is not inspect.Parameter.empty:
            if isinstance(resolved, context.Param):
                raise ValueError(
                    f"Parameter '{param.name}' cannot have"
                    f" a default value; defaults are only"
                    f" supported for input parameters"
                )
            # Plain dtype with default - create In with default
            return context.In(resolved, default=param.default)

        # No default - return as-is
        return resolved

    def _instantiate_func(self, py_func):
        name = py_func.__name__
        sig = inspect.signature(py_func)
        
        # Get return type
        return_annotation = sig.return_annotation
        if return_annotation is inspect.Signature.empty or return_annotation == 'None':
            return_type = type(None)
        else:
            return_type = self._resolve_annotation(return_annotation)

        # Build param definitions, skipping 'sh' parameter
        param_defs = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'sh':
                continue
            param_defs[param_name] = self._resolve_param(param)
        
        func_decl = context.FunctionDecl(
            self, name, return_type, py_func.__doc__
        )
        with func_decl._init_param_defs(**param_defs):
            # Get parameter instances from the function declaration's scope
            params = {pname: getattr(self, pname) for pname in param_defs.keys()}
            # Generate the function body by calling the Python function
            py_func(sh=self, **params)

    def instantiate(self, py_obj):
        if isinstance(py_obj, types.FunctionType):
            self._instantiate_func(py_obj)
        elif isinstance(py_obj, types.ModuleType):
            for func in py_obj._metashade_exports.values():
                self._instantiate_func(func)
