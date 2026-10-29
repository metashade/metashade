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

import metashade.targets._clike.dtypes as clike
import metashade.targets._rtsl.dtypes as rtsl

class Float(clike.Float):
    pass

class Int(clike.Int):
    pass

class Bool(clike.Bool):
    # OSL has no bool type: conditions and comparison results are ints.
    _target_name = 'int'

    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        if isinstance(value, bool):
            return '1' if value else '0'
        return clike.Bool._get_value_ref_static(concrete_cls, value)

# OSL only has 3-component vectors, which support single named components
# but no multi-component swizzles.
class _RawVector3(rtsl.RawVector3):
    _element_type = Float

    def __init__(self, _ = None):
        element_ref = Float._get_value_ref(_)
        super().__init__(
            f'{self.__class__._target_name}({element_ref})'
            if element_ref is not None else _
        )

class Float3(_RawVector3):
    _target_name = 'vector'

class Vector3f(rtsl.Vector3, Float3):
    pass

class Point3f(rtsl.Point3, _RawVector3):
    _target_name = 'point'

class RgbF(rtsl.RgbF, _RawVector3):
    _target_name = 'color'
    _swizzle_str = 'rgb'
