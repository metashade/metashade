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

import metashade._clike.generator as clike

class UniqueRegisterMap:
    def __init__(self, register_type : str):
        self._map = dict()
        self._register_type = register_type

    def add(self, register, value):
        existing = self._map.get(register)
        if existing is not None:
             raise RuntimeError(
                 f'{self._register_type} {register} already used by {existing}'
            )
        self._map[register] = value

class Generator(clike.Generator):
    entry_point = clike.Generator.function
