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

import metashade.rtsl.profile as rtsl

class _StageOutput:
    def __init__(self, dtype, location : int):
        self._dtype = dtype
        self._location = location

class Generator(rtsl.Generator):
    _is_pixel_shader = True

    def __init__(self, file_, glsl_version : str):
        super(Generator, self).__init__(file_)
        self._glsl_version = glsl_version

    def out(dtype, location : int):
        return _StageOutput(dtype, location)
