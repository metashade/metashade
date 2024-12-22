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

import _base
from metashade.hlsl.sm6 import ps_6_0

class TestIf(_base.TestBase):
    def _generate_test_uniforms(self, sh):
        with sh.uniform_buffer(register = 0, name = 'cb'):
            sh.uniform('g_f4A', sh.Float4)
            sh.uniform('g_f4B', sh.Float4)
            sh.uniform('g_f4C', sh.Float4)
            sh.uniform('g_f4D', sh.Float4)

    def test_if(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_test_uniforms(sh)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.entry_point(ctx._entry_point_name, sh.PsOut)():
                sh.result = sh.PsOut()

                with sh.if_(sh.g_f4A.x):
                    sh.result.color = sh.g_f4B
                    sh.return_(sh.result)

                sh.result.color = sh.g_f4C
                sh.return_(sh.result)

    def test_nested_if(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_test_uniforms(sh)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.entry_point(ctx._entry_point_name, sh.PsOut)():
                sh.result = sh.PsOut()

                with sh.if_(sh.g_f4A.x):
                    sh.result.color = sh.g_f4B

                    with sh.if_(sh.g_f4A.y):
                        sh.result.color = sh.g_f4D
                        sh.return_(sh.result)

                    sh.return_(sh.result)

                sh.result.color = sh.g_f4C
                sh.return_(sh.result)

    def test_if_else(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_test_uniforms(sh)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.entry_point(ctx._entry_point_name, sh.PsOut)():
                sh.result = sh.PsOut()

                with sh.if_(sh.g_f4A.x):
                    sh.result.color = sh.g_f4B
                with sh.else_():
                    sh.result.color = sh.g_f4D
                sh.return_(sh.result)

                sh.result.color = sh.g_f4C
                sh.return_(sh.result)
