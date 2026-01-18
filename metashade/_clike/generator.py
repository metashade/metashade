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

import types
import re
from typing import Annotated
import metashade._base.generator as base
from metashade._rtsl.qualifiers import ParamQualifiers, Direction
from . import arrays, context, struct

class Generator(base.Generator):
    def function(self, name : str, return_type = None):
        return context.FunctionDecl(self, name, return_type)

    def struct(self, name):
        return struct.StructDef(self, name)
    
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
                direction = Direction.OUT
            else:
                direction = Direction.INOUT

            return Annotated[inner_type, ParamQualifiers(direction=direction)]

        return getattr(self, annotation)

    def _instantiate_func(self, py_func):
        name = py_func.__name__
        return_annotation = py_func.__annotations__.get('return', 'None')
        
        if return_annotation == 'None':
            return_type = type(None)
        else:
            return_type = self._resolve_annotation(return_annotation)

        param_annotations = {
            name : self._resolve_annotation(annotation)
            for name, annotation in py_func.__annotations__.items()
            if name != 'return'
        }
        func_decl = context.FunctionDecl(
            self, name, return_type, py_func.__doc__
        )
        with func_decl._init_param_defs(**param_annotations):
            # Get parameter instances from the function declaration's scope
            params = { name : getattr(self, name)
                       for name in param_annotations.keys() }
            # Generate the function body by calling the Python function
            py_func(sh = self, **params)

    def instantiate(self, py_obj):
        if isinstance(py_obj, types.FunctionType):
            self._instantiate_func(py_obj)
        elif isinstance(py_obj, types.ModuleType):
            for func in py_obj._metashade_exports.values():
                self._instantiate_func(func)
