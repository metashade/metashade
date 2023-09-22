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

import metashade.rtsl.profile as rtsl
import metashade.clike.struct as struct
from . import data_types
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

class Generator(rtsl.Generator):
    _is_pixel_shader = False

    def __init__(self, file_, matrix_post_multiplication = False):
        super(Generator, self).__init__(file_)
        self._matrix_post_multiplication = matrix_post_multiplication

        self._uniforms_by_semantic = dict()
        self._uniforms_by_register = dict()

        self._register_dtypes(data_types.__name__)
        self._register_dtypes(samplers.__name__)

    def _check_unique_uniform_register(self, register_name : str, new_name :str):
        existing = self._uniforms_by_register.get(register_name)
        if existing is not None:
             raise RuntimeError(
                 f'Uniform register {register_name} already used by {existing}'
            )
        self._uniforms_by_register[register_name] = new_name

    def uniform_buffer(self, register : int, name : str = None):
        self._check_unique_uniform_register(
            register_name = f'b{register}', new_name = name
        )
        return UniformBuffer(self, register = register, name = name)
    
    def uniform(
        self,
        name : str,
        dtype_factory,
        semantic : str = None,
        register : int = None,
        annotations = None
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

        if semantic is not None:
            existing = self._uniforms_by_semantic.get(semantic)
            if existing is not None:
                raise RuntimeError(
                    f"Can't define uniform '{name}' with semantic '{semantic}' "
                    f"because uniform '{existing._name}' already uses that "
                    "semantic."
                )
            
        if register is not None:
            self._check_unique_uniform_register(
                dtype_factory._get_dtype()._format_uniform_register(register),
                name
            )

        value = dtype_factory() #TODO: make it immutable
        self._set_global(name, value)
        self._emit_indent()
        value._define(
            self,
            name,
            semantic = semantic,
            register = register,
            annotations = annotations
        )
        self._emit(';\n')

    def combined_sampler_2d(
        self,
        texture_name : str, texture_register : int,
        sampler_name : str, sampler_register : int,
        texel_type = None,
        cmp = False
    ):
        self._check_public_name(texture_name)   # covered in `uniform`
        self._check_public_name(sampler_name)

        if not self._check_global_scope():
            raise RuntimeError(
                "Uniform textures and samplers "
                "can only be defined at the global scope"
            )

        self._used_texture_registers.check_candidate(texture_register)
        self._used_sampler_registers.check_candidate(sampler_register)

        texture = samplers.Texture2d(
            self,
            texture_name,
            texture_register,
            texel_type
        )
        self._set_global(texture_name, texture)
        self._used_texture_registers.add(texture_register)

        sampler = samplers.Sampler(
            sh = self,
            name = sampler_name,
            register = sampler_register,
            texture = texture,
            cmp = cmp
        )
        self._set_global(sampler_name, sampler)
        self._used_sampler_registers.add(sampler_register)

    def vs_input(self, name):
        return stage_interface.VsInputDef(self, name)
    
    def vs_output(self, name):
        return stage_interface.VsOutputDef(self, name)

    def ps_output(self, name):
        return stage_interface.PsOutputDef(self, name)
