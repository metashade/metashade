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
from typing import Annotated
from dataclasses import dataclass

class Direction(Enum):
    IN = ""
    OUT = "out" 
    INOUT = "inout"

@dataclass
class ParamQualifiers:
    direction: Direction = Direction.IN

# Convenience functions
def Out(base_type: str) -> type:
    """Create an output parameter type"""
    qualifiers = ParamQualifiers(direction=Direction.OUT)
    return Annotated[base_type, qualifiers]

def InOut(base_type: str) -> type:
    """Create an input-output parameter type"""
    qualifiers = ParamQualifiers(direction=Direction.INOUT)
    return Annotated[base_type, qualifiers]