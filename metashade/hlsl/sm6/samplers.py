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

from . import dtypes
import metashade._clike.dtypes as clike_dtypes

# See https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/d3d11-graphics-reference-sm5-objects
# for HLSL 5+ texture object types

class _TextureBase(clike_dtypes.BaseType):
    @classmethod
    def _format_uniform_register(cls, register_idx : int) -> str:
        return f't{register_idx}'

    def __init__(self, texel_type = None):
        super().__init__()
        self._texel_type = texel_type

    def __matmul__(self, sampler):
        return sampler.combine(self)

class Texture1d(_TextureBase):
    _tex_coord_type = dtypes.Float
    _tex_coord_offset_type = dtypes.Int
    _target_name = 'Texture1D'

class Texture2d(_TextureBase):
    _tex_coord_type = dtypes.Float2
    _tex_coord_offset_type = dtypes.Int2
    _target_name = 'Texture2D'

class Texture3d(_TextureBase):
    _tex_coord_type = dtypes.Float3
    _tex_coord_offset_type = dtypes.Int3
    _target_name = 'Texture3D'

class TextureCube(_TextureBase):
    _tex_coord_type = dtypes.Float3
    _target_name = 'TextureCube'

class Sampler(clike_dtypes.BaseType):
    _target_name = 'SamplerState'

    @classmethod
    def _format_uniform_register(cls, register_idx : int) -> str:
        return f's{register_idx}'
    
    def combine(self, texture):
        return CombinedSampler(texture = texture, sampler = self)
    
    def __matmul__(self, texture):
        return self.combine(texture)
    
class SamplerCmp(Sampler):
    _target_name = 'SamplerComparisonState'

class CombinedSampler:
    def __init__(self, texture, sampler):
        self._texture = texture
        self._sampler = sampler

    def __call__(
        self,
        tex_coord,
        offset = None,
        lod = None,
        lod_bias = None,
        cmp_value = None
    ):
        if self._texture is None:
            raise RuntimeError("Sampler hasn't been combined with any texture")
    
        tex_coord_type = self._texture.__class__._tex_coord_type
        if not isinstance(tex_coord, tex_coord_type):
            raise RuntimeError(
                f'Expected texture coordinate type {tex_coord_type}'
            )
        
        args = [self._sampler._name, str(tex_coord)]

        def _handle_offset():
            if offset is not None:
                try:
                    offset_type = \
                        self._texture.__class__._tex_coord_offset_type
                except AttributeError:
                    raise RuntimeError(
                        f"{self._texture.__class__} doesn't support texture "
                        "coordinate offsets"
                    )

                if not isinstance(offset, offset_type):
                    raise RuntimeError(
                        'Expected texture offset coordinate type '
                        + {offset_type}
                    )
                args.append(str(offset))

        def _format(method_name : str) -> str:
            return (
                f'{self._texture._name}.{method_name}('
                + ', '.join(args) + ')'
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
            args.append(str(cmp_value))
            _handle_offset()

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
            return self._sampler._sh.Float(expression + '.r')
        else:
            if cmp_value is not None:
                raise RuntimeError(
                    "Comparison value passed to a non-comparison sampler"
                )
            _handle_offset()

            texel_type = self._texture._texel_type
            if texel_type is None:
                texel_type = self._sampler._sh.Float4

            if lod is not None:
                if lod_bias is not None:
                    raise RuntimeError(
                        "Explicit LOD and LOD bias are mutually exclusive"
                    )
                args.append(str(lod))
                return texel_type(_format('SampleLevel'))
            elif lod_bias is not None:
                args.append(str(lod_bias))
                return texel_type(_format('SampleBias'))
            else:
                return texel_type(_format('Sample'))

