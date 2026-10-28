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

class _OutputQualifierMixin:
    @classmethod
    def _emit_qualifier(cls, sh, qualifier):
        # OSL has a single "output" qualifier for both out and inout
        # parameters, since output parameters are also readable.
        if qualifier:
            sh._emit('output ')

class Float(_OutputQualifierMixin, clike.Float):
    pass

class Int(_OutputQualifierMixin, clike.Int):
    pass

class Bool(_OutputQualifierMixin, clike.Bool):
    # OSL has no bool type: conditions and comparison results are ints.
    _target_name = 'int'

    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        if isinstance(value, bool):
            return '1' if value else '0'
        return clike.Bool._get_value_ref_static(concrete_cls, value)
