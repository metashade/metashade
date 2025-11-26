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

class TestVectorInit:
    @_base.ctx_cls_hg
    def test_vector_init(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('vector_init', sh.Float)():
                sh.f = sh.Float(1)

                sh.f2 = sh.Float2(sh.f)
                sh.f2 = sh.Float2(sh.Float(2))
                sh.f2 = sh.Float2(0)
                sh.f2 = sh.Float2((0, 1))
                sh.f2 = (3, 4)
                sh.f2 = [5, 6]
                sh.f2 = [sh.f, 7]
                sh.f2 = (8, sh.Float(9))

                sh.f3 = sh.Float3(sh.f)
                sh.f3 = sh.Float3(0)
                sh.f3 = sh.Float3(sh.Float(2))
                sh.f3 = sh.Float3((0, 1, 2))
                sh.f3 = [sh.f, sh.Float(3), 4.1]

                sh.p3 = sh.Point3f(sh.f)
                sh.p3 = sh.Point3f(sh.Float(2))
                sh.p3 = sh.Point3f(0)
                sh.p3 = sh.Point3f((0, 1, 0.5))
                sh.p3 = [0.1, sh.f, sh.Float(3)]

                sh.v4 = sh.Vector4f(sh.f)
                sh.v4 = sh.Vector4f(sh.Float(2))
                sh.v4 = sh.Vector4f(0)
                sh.v4 = sh.Vector4f((0, 1, 0.5, 1.0))
                sh.v4 = [0.1, sh.f, sh.Float(3), 1.0]

                sh.rgb = sh.RgbF(sh.f)
                sh.rgb = sh.RgbF(sh.Float(2))
                sh.rgb = sh.RgbF(0)
                sh.rgb = sh.RgbF((0, 1, 0.5))
                sh.rgb = [0.1, sh.f, sh.Float(3)]

                sh.rgba = sh.RgbaF(sh.f)
                sh.rgba = sh.RgbaF(sh.Float(2))
                sh.rgba = sh.RgbaF(0)
                sh.rgba = sh.RgbaF((0, 1, 0.5, 1.0))
                sh.rgba = [0.1, sh.f, sh.Float(3), 1.0]
                sh.rgba = sh.RgbaF(rgb = sh.rgb, a = 0.0)

                sh.return_(sh.f)
