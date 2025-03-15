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

import metashade._base.generator as base
from . import context, struct

class Generator(base.Generator):
    def function(self, name : str, return_type = None):
        return context.FunctionDecl(self, name, return_type)

    def struct(self, name):
        return struct.StructDef(self, name)

    def include(self, file_path : str):
        self._emit(f'#include "{file_path}"\n')

    def if_(self, condition):
        return context.If(self, condition)
    
    def else_(self):
        return context.Else(self)
    
    def _single_line_comment(self, comment):
        self._emit_indent()
        self._emit(f'// {comment}\n')

    def instantiate(self, func):
        name = func.__name__

        return_type = func.__annotations__['return']
        return_type = getattr(self, return_type)

        args = {
            name : getattr(self, annotation)
            for name, annotation in func.__annotations__.items()
            if name != 'return'
        }
        decl = context.FunctionDecl(self, name, return_type)
        with decl(**args):
            # Import the parameters into the current scope
            locals_ = locals()
            locals_.update({ name : getattr(self, name) for name in args.keys() })
            func(self, **args)
