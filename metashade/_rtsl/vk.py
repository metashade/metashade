
"""
Vulkan-related functionality common between HLSL and GLSL backends.
"""

# Copyright 2025 Pavlo Penenko
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
from .generator import UniqueKeyChecker

class UniqueInputLocationChecker(UniqueKeyChecker):
    @staticmethod
    def _format_error_message(location, existing_value):
        return (
            f'Vulkan input location {location} '
            f'is already in use by {existing_value}'
        )

class UniqueOutputLocationChecker(UniqueKeyChecker):
    @staticmethod
    def _format_error_message(location, existing_value):
        return (
            f'Vulkan output location {location} '
            f'is already in use by {existing_value}'
        )

class UniqueBindingChecker(UniqueKeyChecker):
    class SetBindingPair(NamedTuple):
        set : int
        binding : int

    @staticmethod
    def _format_error_message(set_binding : SetBindingPair, existing_value):
        return (
            f'Vulkan uniform binding {set_binding.binding} in descriptor set '
            f'{set_binding.set} is already in use by {existing_value}'
        )
