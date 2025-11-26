# Copyright 2023 Pavlo Penenko
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

class TestDTypes:
    @_base.ctx_cls_hg
    def test_init_from_literal(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('test', sh.Float)():
                sh.f4A = sh.Float4(1.0)
                sh.f4B = sh.Float4(0.0) - sh.f4A
                
                sh.f3A = sh.Float3(0.0)
                sh.f3B = sh.f3A + sh.Float3(1.0)

                sh.f2A = sh.Float2(0.6578467)
                sh.f2B = sh.Float2(0.4235) * sh.f2A

                sh.fA = sh.Float(1.0)
                sh.fB = sh.Float(2.0) + sh.fA

                sh.return_(sh.f4B.w + sh.f3B.z + sh.f2B.y + sh.fB)
