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

from abc import ABC, abstractmethod
import metashade._clike.generator as clike
from .qualifiers import Out, InOut

class UniqueKeyChecker(ABC):
    def __init__(self):
        self._map = dict()

    @staticmethod
    @abstractmethod
    def _format_error_message(register, existing_value):
        pass

    def add(self, key, value):
        existing_value = self._map.get(key)
        if existing_value is not None:
             raise RuntimeError(
                 self._format_error_message(key, existing_value)
            )
        self._map[key] = value

class Generator(clike.Generator, ABC):
    entry_point = clike.Generator.function

    @abstractmethod
    def uniform_buffer(
        self,
        name : str,
        dx_register: int,
        vk_set : int,
        vk_binding : int
    ):
        pass

    def Out(self, base_type):
        """Create an output parameter type for function signatures"""
        return Out(base_type)
    
    def InOut(self, base_type):
        """Create an input-output parameter type for function signatures"""
        return InOut(base_type)
