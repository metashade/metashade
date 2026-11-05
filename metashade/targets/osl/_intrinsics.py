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
OSL intrinsic function mixins.

This module provides OSL implementations of the intrinsic functions that
are used by metashade.std, matching the GLSL ones. OSL's math functions
accept both float and 3-component types.
"""


class FloatIntrinsicsMixin:
    """Mixin providing float intrinsic methods for OSL types."""

    def floor(self):
        """Floor value."""
        return self._sh._instantiate_dtype(
            self.__class__,
            f'floor({self})'
        )

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

    def lerp(self, a, b):
        """Linear interpolation: mix(a, b, self)."""
        return self._sh._instantiate_dtype(
            a.__class__,
            f'mix({a}, {b}, {self})'
        )

    def saturate(self):
        """Clamp value to range [0, 1]. OSL polyfill using clamp."""
        return self.clamp(0.0, 1.0)

    def sqrt(self):
        """Square root."""
        return self._sh._instantiate_dtype(
            self.__class__,
            f'sqrt({self})'
        )

    def sin(self):
        return self._sh._instantiate_dtype(
            self.__class__, f'sin({self})'
        )

    def cos(self):
        return self._sh._instantiate_dtype(
            self.__class__, f'cos({self})'
        )

    def radians(self):
        return self._sh._instantiate_dtype(
            self.__class__, f'radians({self})'
        )
