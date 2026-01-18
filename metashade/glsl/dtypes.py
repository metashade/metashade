# Copyright 2024 Pavlo Penenko
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

import numbers
import metashade._rtsl.dtypes as rtsl
from . import _intrinsics


class Float(_intrinsics.FloatIntrinsicsMixin, rtsl.Float):
    pass

class Int(rtsl.Int):
    pass

class _RawVector(rtsl._RawVector):
    def __init__(self, _ = None):
        element_ref = self.__class__._element_type._get_value_ref(_)

        super().__init__(
            f'{self.__class__._target_name}({element_ref})'
            if element_ref is not None else _
        )

class _RawVectorF(_intrinsics.FloatIntrinsicsMixin, _RawVector, rtsl._RawVectorF):
    _element_type = Float
    
class _RawVectorI(_RawVector):
    _element_type = Int

class Float2(rtsl.RawVector2, _RawVectorF):
    _target_name = 'vec2'

class Float3(rtsl.RawVector3, _RawVectorF):
    _target_name = 'vec3'

class Float4(rtsl.RawVector4, _RawVectorF):
    _target_name = 'vec4'

class Int2(rtsl.RawVector2, _RawVectorI):
    _target_name = 'ivec2'

class Int3(rtsl.RawVector3, _RawVectorI):
    _target_name = 'ivec3'

class Int4(rtsl.RawVector4, _RawVectorI):
    _target_name = 'ivec4'

# TODO: share the below implementations with HLSL?
class Vector4f(rtsl.Vector4, Float4):
    pass

class Vector2f(rtsl.Vector2, Float2):
    pass

class Vector3f(rtsl.Vector3, Float3):
    pass

class Point2f(rtsl.Point2, Float2):
    pass

class Point3f(rtsl.Point3, Float3):
    pass

class RgbF(rtsl.RgbF, Float3):
    _swizzle_str = 'rgb'

class RgbaF(rtsl.RgbaF, Float4):
    _swizzle_str = 'rgba'
