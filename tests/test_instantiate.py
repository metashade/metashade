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
            sh.uniform('g_f4C', sh.Float4)

    def _generate_ps_main_decl(self, sh, ctx : _base._TestContext):
        if isinstance(ctx, _base.HlslTestContext):
            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)
            return sh.entry_point(ctx._entry_point_name, sh.PsOut)()
        else:
            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)
            return sh.entry_point(ctx._entry_point_name)()

    @_base.ctx_cls_hg
    def test_instantiate_py_func(self, ctx_cls):
        ctx = ctx_cls()
        with ctx as sh:
            self._generate_test_uniforms(sh)
            sh.instantiate(_py_add)

            with self._generate_ps_main_decl(sh, ctx):
                sh.c = sh._py_add(a = sh.g_f4A, b = sh.g_f4B)

                if isinstance(ctx, _base.HlslTestContext):
                    sh.result = sh.PsOut()
                    sh.result.color = sh.c
                    sh.return_(sh.result)
                else:
                    sh.out_f4Color = sh.c

    @_base.ctx_cls_hg
    def test_instantiate_py_module(self, ctx_cls):
        import _exports

        ctx = ctx_cls()
        with ctx as sh:
            self._generate_test_uniforms(sh)
            sh.instantiate(_exports)

            with self._generate_ps_main_decl(sh, ctx):
                sh.c = sh.py_madd(
                    a = sh.g_f4A, b = sh.g_f4B, c = sh.g_f4C
                )

                if isinstance(ctx, _base.HlslTestContext):
                    sh.result = sh.PsOut()
                    sh.result.color = sh.c
                    sh.return_(sh.result)
                else:
                    sh.out_f4Color = sh.c
