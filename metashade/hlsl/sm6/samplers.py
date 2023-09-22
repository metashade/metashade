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
import metashade.clike.data_types as clike_dtypes

class Texture2d(clike_dtypes.BaseType):
    _tex_coord_type = data_types.Float2
    _target_name = 'Texture2D'

    @classmethod
    def _format_uniform_register(cls, register_idx : int) -> str:
        return f't{register_idx}'

    def __init__(self, texel_type = None):
        super().__init__()
        self._texel_type = texel_type

class Sampler(clike_dtypes.BaseType):
    _target_name = 'SamplerState'

    @classmethod
    def _format_uniform_register(cls, register_idx : int) -> str:
        return f's{register_idx}'

    def __call__(self, texture):
        return CombinedSampler(texture = texture, sampler = self)
    
class SamplerCmp(Sampler):
    _target_name = 'SamplerComparisonState'

class CombinedSampler(clike_dtypes.BaseType):
    def __init__(self, texture, sampler):
        self._texture = texture
        self._sampler = sampler

    def __call__(self, tex_coord, lod = None, lod_bias = None, cmp_value = None):
        if self._texture is None:
            raise RuntimeError("Sampler hasn't been combined with any texture")
    
        tex_coord_type = self._texture.__class__._tex_coord_type
        if not isinstance(tex_coord, tex_coord_type):
            raise RuntimeError(
                f'Expected texture coordinate type {tex_coord_type}'
            )
        
        if isinstance(self._sampler, SamplerCmp):   #TODO: refactor
            if lod_bias is not None:
                raise RuntimeError(
                    "Comparison samplers don't support LOD bias"
                )
            if self._texture._texel_type is not None:
                raise RuntimeError(
                    "Comparison samplers don't support custom texel types"
                )
            if cmp_value is None:
                raise RuntimeError(
                    "Missing sampler comparison value"
                )
            
            def _format(method_name : str) -> str:
                return (
                    f'{self._texture._name}.{method_name}'
                    + f'({self._sampler._name}, {tex_coord}, {cmp_value}).r'
                )
            if lod is not None:
                if lod == 0:
                    expression = _format('SampleCmpLevelZero')
                else:
                    raise RuntimeError(
                        "Only LOD 0 can be explicitly sampled"
                        " by comparison samplers"
                    )
            else:
                expression = _format('SampleCmp')
            return self._sampler._sh.Float(expression)
        else:
            if cmp_value is not None:
                raise RuntimeError(
                    "Comparison value passed to a non-comparison sampler"
                )
            texel_type = self._texture._texel_type
            if texel_type is None:
                texel_type = self._sampler._sh.Float4

            if lod is not None:
                if lod_bias is not None:
                    raise RuntimeError(
                        "Explicit LOD and LOD bias are mutually exclusive"
                    )
                return texel_type(
                    _ = f'{self._texture._name}.SampleLevel({self._sampler._name}, {tex_coord}, {lod})'
                )
            elif lod_bias is not None:
                return texel_type(
                    _ = f'{self._texture._name}.SampleBias({self._sampler._name}, {tex_coord}, {lod_bias})'
                )
            else:
                return texel_type(
                    _ = f'{self._texture._name}.Sample({self._sampler._name}, {tex_coord})'
                )
