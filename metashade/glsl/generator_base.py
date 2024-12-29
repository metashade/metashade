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

from metashade._base.dtypes import BaseType
import metashade._rtsl.generator as rtsl
from . import dtypes
from .stage_interface import StageIO, StageInput, StageOutput

class UniformBuffer:
    def __init__(self, sh, set : int, binding : int, name : str = None):
        self._sh = sh
        self._name = name
        self._set = set
        self._binding = binding

    def __enter__(self):
        self._sh._emit(
            f'layout (set = {self._set}, binding = {self._set}) '
            f'uniform {self._name}\n{{\n'
        )
        self._sh._push_indent()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_indent()
        self._sh._emit('};\n\n')

class Generator(rtsl.Generator):
    def __init__(self, file_, glsl_version : str):
        super(Generator, self).__init__(file_)
        self._glsl_version = glsl_version

        # Register the data types
        # TODO: share with other shader stages
        self._register_dtypes(dtypes.__name__)
        self._emit(f'#version {glsl_version}\n')

        self._io_locations_by_cls = {
            io_cls.__name__ : set() for io_cls in [StageInput, StageOutput]
        }

    def _create_stage_io(self, io_cls, dtype, location : int):
        locations_in_use = self._io_locations_by_cls[io_cls.__name__]
        if location in locations_in_use:
            raise RuntimeError(
                f'Location {location} is already in use'
            )
        locations_in_use.add(location)
        return io_cls(dtype, location)

    def stage_input(self, dtype, location : int):
        return self._create_stage_io(StageInput, dtype, location)

    def stage_output(self, dtype, location : int):
        return self._create_stage_io(StageOutput, dtype, location)
    
    def uniform_buffer(self, set : int, binding : int, name : str = None):
        return UniformBuffer(self, set = set, binding = binding, name = name)
    
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

            # Define the stage output
            value._define(self, name)
        else:
            super().__setattr__(name, value)
