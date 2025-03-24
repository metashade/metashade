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

def _py_add(sh, a : 'Float4', b : 'Float4') -> 'Float4':
    sh.c = a + b
    sh.return_(sh.c)

class TestInstantiate(_base.TestBase):
    def _generate_test_uniforms(self, sh):
        with sh.uniform_buffer(
            name = 'cb',
            dx_register = 0,
            vk_set = 0,
            vk_binding = 0
        ):
            sh.uniform('g_f4A', sh.Float4)
            sh.uniform('g_f4B', sh.Float4)

    def test_instantiate_py_func(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_test_uniforms(sh)
            sh.instantiate(_py_add)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.entry_point(ctx._entry_point_name, sh.PsOut)():
                sh.result = sh.PsOut()
                sh.result.color = sh._py_add(a = sh.g_f4A, b = sh.g_f4B)
                sh.return_(sh.result)

    def test_instantiate_py_module(self):
        import _exports

        print(_exports._metashade_exports)

        # ctx = _base.HlslTestContext()
        # with ctx as sh:
        #     self._generate_test_uniforms(sh)
        #     sh.instantiate(_py_add)

        #     with sh.ps_output('PsOut') as PsOut:
        #         PsOut.SV_Target('color', sh.Float4)

        #     with sh.entry_point(ctx._entry_point_name, sh.PsOut)():
        #         sh.result = sh.PsOut()
        #         sh.result.color = sh.py_add(a = sh.g_f4A, b = sh.g_f4B)
        #         sh.return_(sh.result)
