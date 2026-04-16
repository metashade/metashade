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

from enum import Enum
from typing import Annotated, Any
from dataclasses import dataclass

_NO_DEFAULT = object()

class Direction(Enum):
    IN = ""
    OUT = "out" 
    INOUT = "inout"

@dataclass
class ParamQualifiers:
    direction: Direction = Direction.IN
    default: Any = _NO_DEFAULT

# Convenience functions
def In(base_type: str, default: Any = _NO_DEFAULT, **kwargs) -> type:
    """Create an input parameter type"""
    qualifiers = ParamQualifiers(direction=Direction.IN, default=default, **kwargs)
    return Annotated[base_type, qualifiers]

def Out(base_type: str, default: Any = _NO_DEFAULT, **kwargs) -> type:
    """Create an output parameter type"""
    qualifiers = ParamQualifiers(direction=Direction.OUT, default=default, **kwargs)
    return Annotated[base_type, qualifiers]

def InOut(base_type: str, default: Any = _NO_DEFAULT, **kwargs) -> type:
    """Create an input-output parameter type"""
    qualifiers = ParamQualifiers(direction=Direction.INOUT, default=default, **kwargs)
    return Annotated[base_type, qualifiers]