# Copyright 2024 Pavlo Penenko
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

from typing import NamedTuple
from metashade._base.dtypes import BaseType, check_valid_index
import metashade._rtsl.generator as rtsl
from . import dtypes

from .stage_interface import (
    StageIO, StageInput, StageOutput
)

from metashade._rtsl.vk import (
    UniqueOutputLocationChecker, UniqueInputLocationChecker
)

class UniformBuffer:
    def __init__(self, sh, set : int, binding : int, name : str = None):
        self._sh = sh
        self._name = name
        self._set = set
        self._binding = binding

    def __enter__(self):
        self._sh._emit(
            f'layout (set = {self._set}, binding = {self._binding}) '
            f'uniform {self._name}\n{{\n'
        )
        self._sh._push_indent()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_indent()
        self._sh._emit('};\n\n')

class _UniqueBindingChecker(rtsl.UniqueKeyChecker):
    class SetBindingPair(NamedTuple):
        set : int
        binding : int

    @staticmethod
    def _format_error_message(set_binding : SetBindingPair, existing_value):
        return (
            f'Uniform binding {set_binding.binding} in descriptor set '
            f'{set_binding.set} is already in use by {existing_value}'
        )

class Generator(rtsl.Generator):
    def __init__(self, file_, glsl_version : str):
        super(Generator, self).__init__(file_)
        self._glsl_version = glsl_version

        # Register the data types
        # TODO: share with other shader stages
        self._register_dtypes(dtypes.__name__)
        self._emit(f'#version {glsl_version}\n')

        self._unique_location_checkers = {
            StageInput.__name__: UniqueInputLocationChecker(),
            StageOutput.__name__: UniqueOutputLocationChecker()
        }

        self._unique_binding_checker = _UniqueBindingChecker()

    def stage_input(self, dtype, location : int):
        return StageInput(dtype, location)

    def stage_output(self, dtype, location : int):
        return StageOutput(dtype, location)
    
    def uniform_buffer(
        self,
        name : str,
        vk_set : int,
        vk_binding : int,
        dx_register: int = None
    ):
        check_valid_index(vk_set)
        check_valid_index(vk_binding)
        self._unique_binding_checker.add(
            _UniqueBindingChecker.SetBindingPair(vk_set, vk_binding),
            name
        )
        return UniformBuffer(
            self, set = vk_set, binding = vk_binding, name = name
        )

    def uniform(
        self,
        name : str,
        dtype_factory
    ):
        self._check_public_name(name)
        if not self._check_global_scope():
            raise RuntimeError(
                "Uniforms can only be defined at the global scope"
            )

        #TODO: make it immutable
        value = ( dtype_factory if isinstance(dtype_factory, BaseType)
            else dtype_factory()
        )

        self._set_global(name, value)
        self._emit_indent()
        value._define(
            self,
            name
        )
        self._emit(';\n')
    
    def __setattr__(self, name, value):
        if isinstance(value, StageIO):
            if not self._check_global_scope():
                raise RuntimeError(
                    'Stage inputs and outputs '
                    'can only be defined at global scope'
                )
            location_checker = self._unique_location_checkers[
                value.__class__.__name__
            ]
            value._define(self, name, location_checker)
        else:
            super().__setattr__(name, value)
