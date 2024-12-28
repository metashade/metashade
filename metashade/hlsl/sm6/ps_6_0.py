# Copyright 2021 Pavlo Penenko
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

from . import generator_base, stage_interface

class Generator(generator_base.Generator):
    _is_pixel_shader = True

    def vs_output(self, name):
        return stage_interface.VsOutputDef(self, name)

    def ps_output(self, name):
        return stage_interface.PsOutputDef(self, name)