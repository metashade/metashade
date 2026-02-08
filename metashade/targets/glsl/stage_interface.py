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

import metashade.targets._rtsl.generator as rtsl
from metashade.targets._base.dtypes import check_valid_index

class StageIO:
    def __init__(self, dtype, location : int):
        check_valid_index(location)
        self._dtype_factory = dtype
        self._location = location

    def _define(self, sh, name, location_checker):
        location_checker.add(self._location, name)
        value = self._dtype_factory()
        sh._set_global(name, value)
        value._bind(sh, name, allow_init = False)
        sh._emit(
            f'layout(location = {self._location}) {self._inout_keyword} '
            f'{value.__class__._get_target_type_name()} {value._name};\n'
        )

class StageOutput(StageIO):
    _inout_keyword = 'out'

class StageInput(StageIO):
    #TODO: make it immutable
    _inout_keyword = 'in'
