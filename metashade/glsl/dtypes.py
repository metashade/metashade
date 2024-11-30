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

import metashade._rtsl.dtypes as rtsl

class Float(rtsl.Float):
    pass

class Int(rtsl.Int):
    pass

class _RawVector(rtsl._RawVector):
    def __init__(self, _ = None):
        element_ref = self.__class__._element_type._get_value_ref(_)
        super().__init__(
            '.'.join((str(element_ref), 'x' * self.__class__._dim))
                if element_ref is not None else _
        )

class _RawVectorF(_RawVector):
    _element_type = Float

    def normalize(self):
        return self.__class__( f'normalize({self})' )

    def length(self):
        return self._sh._instantiate_dtype(
            self.__class__._element_type,
            f'length({self})'
        )
    
    def reflect(self, rhs):
        return self.__class__( f'reflect({self}, {rhs})' )
    
class _RawVectorI(_RawVector):
    _element_type = Int

class Float2(_RawVectorF, rtsl.RawVector2):
    _target_name = 'vec2'

class Float3(_RawVectorF, rtsl.RawVector3):
    _target_name = 'vec3'

class Float4(_RawVectorF, rtsl.RawVector4):
    _target_name = 'vec4'

    def __init__(self, _ = None, xyz = None, w = None):
        # TODO: share the implementation with HLSL?
        if xyz is None:
            if w is not None:
                raise RuntimeError('Conflicting arguments')

            super().__init__(_)
        else:
            if _ is not None:
                raise RuntimeError('Conflicting arguments')

            xyz = Float3._get_value_ref(xyz)
            if xyz is None:
                raise RuntimeError('"xyz" must be convertible to Float3')

            if not isinstance(w, numbers.Number):
                raise RuntimeError('"w" must be a scalar number')

            expression = '{dtype}({xyz}, {w})'.format(
                dtype = self.__class__._target_name,
                xyz = xyz,
                w = w
            )
            super().__init__(expression)

class Int1(_RawVectorI, rtsl.RawVector1):
    _target_name = 'int1'

class Int2(_RawVectorI, rtsl.RawVector2):
    _target_name = 'int2'

class Int3(_RawVectorI, rtsl.RawVector3):
    _target_name = 'int3'

class Int4(_RawVectorI, rtsl.RawVector4):
    _target_name = 'int4'

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

    def __init__(self, _ = None, rgb = None, a = None):
        if ( isinstance(rgb, Float3) and not isinstance(rgb, RgbF) ):
            raise RuntimeError('"rgb" must be convertible to RgbF')

        super().__init__(_ = _, xyz = rgb, w = a)

    def __getattr__(self, name):
        if name == 'rgb':
            return self._sh._instantiate_dtype(
                RgbF,
                '.'.join((str(self), name))
            )
        else:
            return super().__getattr__(name)

    def __setattr__(self, name, value):
        if name == 'rgb':
            lvalue = self._sh._instantiate_dtype(
                RgbF,
                '.'.join((str(self), name))
            )
            lvalue._assign(value)
        else:
            super().__setattr__(name, value)
