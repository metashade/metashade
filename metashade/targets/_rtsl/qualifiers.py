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

from typing import Annotated, Any

class _ParamDirection:
    """Base class for parameter direction markers in Annotated metadata."""
    value: str

class _In(_ParamDirection):
    """Input parameter direction. Only inputs can have defaults."""
    value = ""
    def __init__(self, default=None):
        self.default = default

class _Out(_ParamDirection):
    """Output parameter direction."""
    value = "out"

class _InOut(_ParamDirection):
    """Input-output parameter direction."""
    value = "inout"

# Convenience functions
def In(base_type: Any, default: Any = None) -> type:
    """Create an input parameter type"""
    return Annotated[base_type, _In(default=default)]

def Out(base_type: Any) -> type:
    """Create an output parameter type"""
    return Annotated[base_type, _Out()]

def InOut(base_type: Any) -> type:
    """Create an input-output parameter type"""
    return Annotated[base_type, _InOut()]