# Copyright 2020 Pavlo Penenko
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

from . import data_types

class Texture2d:
    _tex_coord_type = data_types.Float2

    def __init__(self, sh, name : str, register : int, texel_type = None):
        self._name = name
        self._sh = sh
        self._texel_type = texel_type
        sh._emit( f'Texture2D {name} : register(t{register});\n' )

class Sampler:
    def __init__(self, sh, name : str, register : int, cmp : bool, texture):
        self._sh = sh
        self._name = name
        self._cmp = cmp
        self._texture = texture
        object_name = 'SamplerComparisonState' if cmp else 'SamplerState'
        sh._emit( f'{object_name} {name} : register(s{register});\n\n' )

    def __call__(self, tex_coord, compare_value = None):
        if self._texture is None:
            raise RuntimeError("Sampler hasn't been combined with any texture")
    
        tex_coord_type = self._texture.__class__._tex_coord_type
        if not isinstance(tex_coord, tex_coord_type):
            raise RuntimeError(
                f'Expected texture coordinate type {tex_coord_type}'
            )
        
        if self._cmp:
            if self._texture._texel_type is not None:
                raise RuntimeError(
                    "Comparison samplers don't support custom texel types"
                )
            if compare_value is None:
                raise RuntimeError(
                    "Missing sampler comparison value"
                )
            return self._sh.Float(
                f'{self._texture._name}.SampleCmp({self._name}, {tex_coord}, {compare_value}).r'
            )
        else:
            if compare_value is not None:
                raise RuntimeError(
                    "Comparison value passed to a non-comparison sampler"
                )
            texel_type = self._texture._texel_type
            if texel_type is None:
                texel_type = self._sh.Float4

            return texel_type(
                _ = f'{self._texture._name}.Sample({self._name}, {tex_coord})'
            )
