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

import metashade._rtsl.profile as rtsl
from . import dtypes
from .stage_interface import StageOutput

class Generator(rtsl.Generator):
    _is_pixel_shader = True

    def __init__(self, file_, glsl_version : str):
        super(Generator, self).__init__(file_)
        self._glsl_version = glsl_version

        # Register the data types
        # TODO: share with other shader stages
        self._register_dtypes(dtypes.__name__)
        self._emit(f'#version {glsl_version}\n')

    def out(self, dtype, location : int):
        return StageOutput(dtype, location)
    
    def __setattr__(self, name, value):
        if isinstance(value, StageOutput):
            if not self._check_global_scope():
                raise RuntimeError(
                    "Stage outputs can only be defined at global scope"
                )
            # Define the stage output
            value._define(self, name)
        else:
            super().__setattr__(name, value)
        
