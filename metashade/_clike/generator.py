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
import metashade._base.generator as base
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

    def _instantiate_func(self, func):
        name = func.__name__

        return_annotation = func.__annotations__['return']
        
        if return_annotation == 'None':
            return_type = type(None)
        else:
            return_type = getattr(self, return_annotation)

        args = {
            name : getattr(self, annotation)
            for name, annotation in func.__annotations__.items()
            if name != 'return'
        }
        decl = context.FunctionDecl(self, name, return_type)
        with decl(**args):
            args = { name : getattr(self, name) for name in args.keys() }
            func(sh = self, **args)

    def instantiate(self, py_obj):
        if isinstance(py_obj, types.FunctionType):
            self._instantiate_func(py_obj)
        elif isinstance(py_obj, types.ModuleType):
            for func in py_obj._metashade_exports.values():
                self._instantiate_func(func)
