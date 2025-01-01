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

from metashade._base.dtypes import BaseType, check_valid_index
import metashade._rtsl.generator as rtsl
from . import dtypes
from . import samplers

class UniformBuffer:
    def __init__(self, sh, register : int, name : str = None):
        self._sh = sh
        self._name = name
        self._register = register

    def __enter__(self):
        self._sh._emit('cbuffer')

        if self._name is not None:
            self._sh._emit(' ')
            self._sh._emit(self._name)

        self._sh._emit( f' : register(b{self._register})\n{{\n' )
        self._sh._push_indent()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_indent()
        self._sh._emit('};\n\n')

class _UniqueRegisterChecker(rtsl.UniqueKeyChecker):
    @staticmethod
    def _format_error_message(register, existing_value):
        return (
            f'Uniform register {register} is already in use by {existing_value}'
        )

class Generator(rtsl.Generator):
    _is_pixel_shader = False

    def __init__(self, file_, matrix_post_multiplication = False):
        super(Generator, self).__init__(file_)
        self._matrix_post_multiplication = matrix_post_multiplication

        self._uniforms_by_register = _UniqueRegisterChecker('Uniform register')

        self._register_dtypes(dtypes.__name__)
        self._register_dtypes(samplers.__name__)

    def uniform_buffer(self, register : int, name : str = None):
        check_valid_index(register)
        self._uniforms_by_register.add(f'b{register}', name)
        return UniformBuffer(self, register = register, name = name)
    
    def uniform(
        self,
        name : str,
        dtype_factory,
        register : int = None
    ):
        '''
        https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-variable-syntax
        # TODO: packoffset
        '''
        self._check_public_name(name)
        if not self._check_global_scope():
            raise RuntimeError(
                "Uniforms can only be defined at the global scope"
            )

        if register is not None:
            check_valid_index(register)
            self._uniforms_by_register.add(
                dtype_factory._get_dtype()._format_uniform_register(register),
                name
            )

        #TODO: make it immutable
        value = ( dtype_factory if isinstance(dtype_factory, BaseType)
            else dtype_factory()
        )

        self._set_global(name, value)
        self._emit_indent()
        value._define(
            self,
            name,
            register = register
        )
        self._emit(';\n')

    def vs_input(self, name):
        return stage_interface.VsInputDef(self, name)
    
    def vs_output(self, name):
        return stage_interface.VsOutputDef(self, name)

    def ps_output(self, name):
        return stage_interface.PsOutputDef(self, name)
