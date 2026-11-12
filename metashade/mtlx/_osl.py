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
Data types defined by MaterialX's OSL includes rather than by OSL itself.
"""

import metashade.targets._rtsl.dtypes as rtsl
from metashade.targets.osl import dtypes as osl_dtypes

class Float2(rtsl.RawVector2):
    '''
    OSL has no 2-component vector, so MaterialX's OSL includes define a
    ``vector2`` struct and overload the arithmetic operators for it.
    '''
    _target_name = 'vector2'
    _element_type = osl_dtypes.Float

    @classmethod
    def _get_related_type(cls, dim : int):
        if dim != 1:
            raise AttributeError(
                f'vector2 has no {dim}-component swizzles, only x and y'
            )
        return cls._element_type
