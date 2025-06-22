# Copyright 2025 Pavlo Penenko
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

import _base

def _func(sh) -> 'Float':
    sh.arr = sh.array(sh.Float4, (2))()
    # sh.array[0] = sh.Float4(1.0)
    # sh.array[1] = sh.Float4(0.0)
    # sh.f4A = sh.array[0] + sh.array[1]

    sh.return_(sh.f4A)

class TestArrays(_base.TestBase):
    @_base.ctx_cls_hg
    def test_arrays(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            sh.instantiate(_func)
