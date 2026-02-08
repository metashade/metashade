# Copyright 2026 Pavlo Penenko
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

"""
GLSL intrinsic function mixins.

This module provides GLSL-specific implementations of intrinsic functions
that are used by metashade.std. Where HLSL and GLSL differ (e.g., saturate),
this module provides the appropriate GLSL equivalent.
"""


class FloatIntrinsicsMixin:
    """Mixin providing float intrinsic methods for GLSL types."""

    def clamp(self, min_val, max_val):
        """Clamp value to range [min_val, max_val]."""
        return self._sh._instantiate_dtype(
            self.__class__,
            f'clamp({self}, {min_val}, {max_val})'
        )

    def pow(self, y):
        """Raise to power y."""
        return self._sh._instantiate_dtype(
            self.__class__,
            f'pow({self}, {y})'
        )

    def saturate(self):
        """Clamp value to range [0, 1]. GLSL polyfill using clamp."""
        return self.clamp(0.0, 1.0)

    def sqrt(self):
        """Square root."""
        return self._sh._instantiate_dtype(
            self.__class__,
            f'sqrt({self})'
        )
