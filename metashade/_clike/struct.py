# Copyright 2018 Pavlo Penenko
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

from metashade._clike.dtypes import BaseType

class StructMemberDef:
    def __init__(self, dtype, semantic = None):
        self.dtype = dtype
        self.semantic = semantic

class StructBase:
    def __init__(self, expression : str = None):
        for member_name, member_def in self.__class__._member_defs.items():
            member_expression = ( None if expression is None
                else '.'.join((expression, member_name))
            )
            setattr(self, member_name, member_def.dtype(member_expression))
        self._constructed = True

    def _bind_members(self, sh, struct_instance_name):
        for member_name, member in vars(self).items():
            if not member_name.startswith('_'):
                nested_name = '.'.join([struct_instance_name, member_name])
                member._bind(sh, nested_name, allow_init = True)
    
    def _set_member(self, name, value):
        if name.startswith('_') or not hasattr(self, '_constructed'):
            return False

        member = getattr(self, name)
        if isinstance(member, BaseType):
            member._assign(value)
        else:
            raise RuntimeError(
                "Metashade struct members "
                "can't be added or redefined after construction"
            )
        return True

class Struct(BaseType, StructBase):
    def __init__(self, expression : str = None):
        BaseType.__init__(self, expression)
        StructBase.__init__(self, expression)

        self._sh = self.__class__._sh
        for member_name, member in vars(self).items():
            if not member_name.startswith('_'):
                member._set_generator(self._sh)

    def _bind(self, sh, identifier, allow_init):
        super()._bind(sh, identifier, allow_init)
        self._bind_members(sh, identifier)

    def __setattr__(self, name, value):
        if not self._set_member(name, value):
            super().__setattr__(name, value)

def define_struct(sh, name, member_defs):
    struct_type = type(
        name,
        (Struct,),
        {
            '_sh' : sh,
            '_member_defs' : member_defs
        }
    )
    sh._set_global(name, struct_type)

    sh._emit(f'struct {name}\n{{\n')
    sh._push_indent()

    for member_name, member_def in member_defs.items():
        sh._emit_indent()
        member_def.dtype._emit_def(sh, member_name, member_def.semantic)
        sh._emit(";\n")

    sh._pop_indent()
    sh._emit('};\n\n')

class StructDef:
    def __init__(self, sh, name):
        self._sh = sh
        self._name = name

    def __call__(self, **kwargs):
        define_struct(
            self._sh,
            self._name,
            {
                name : StructMemberDef(dtype_factory._get_dtype())
                for name, dtype_factory in kwargs.items()
            }
        )

