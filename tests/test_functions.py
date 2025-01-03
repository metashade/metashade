# Copyright 2022 Pavlo Penenko
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

import pytest, _base
from metashade.hlsl.sm6 import ps_6_0

class TestFunctions(_base.TestBase):
    def _generate_add_func(self, sh, decl_only = False):
        func = sh.function('add', sh.Float4)(a = sh.Float4, b = sh.Float4)

        # Test that we don't leak the scope created for the parameters
        assert getattr(sh, 'a', None) is None

        if decl_only:
            func.declare()
        else:
            with func:
                sh.return_(sh.a + sh.b)

    def _generate_test_uniforms(self, sh):
        with sh.uniform_buffer(dx_register = 0, name = 'cb'):
            sh.uniform('g_f4A', sh.Float4)
            sh.uniform('g_f4B', sh.Float4)
            sh.uniform('g_f3C', sh.Float3)

    def _generate_ps_main(self, sh, ctx : _base._TestContext):
        with sh.ps_output('PsOut') as PsOut:
            PsOut.SV_Target('color', sh.Float4)

        return sh.entry_point(ctx._entry_point_name, sh.PsOut)()

    def _correct_ps_main(self, sh, ctx : _base._TestContext):
        self._generate_test_uniforms(sh)
        with self._generate_ps_main(sh, ctx):
            sh.result = sh.PsOut()
            sh.result.color = sh.add(a = sh.g_f4A, b = sh.g_f4B)
            sh.return_(sh.result)

    def test_function_call(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_add_func(sh)
            self._correct_ps_main(sh, ctx)

    def test_kwarg_reorder(self):
        ctx = _base.HlslTestContext(as_lib = True)
        with ctx as sh:
            self._generate_test_uniforms(sh)

            sh.function('func', sh.Float4)(
                a = sh.Float4, c = sh.Float3
            ).declare()

            with self._generate_ps_main(sh, ctx):
                sh.result = sh.PsOut()
                sh.result.color = sh.func(c = sh.g_f3C, a = sh.g_f4A)
                sh.return_(sh.result)

    def test_function_decl_call(self):
        ctx = _base.HlslTestContext(as_lib = True)
        with ctx as sh:
            self._generate_add_func(sh, decl_only = True)
            self._correct_ps_main(sh, ctx)

    def test_included_function_call(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            sh.include('include/add.hlsl')
            self._generate_add_func(sh, decl_only = True)
            self._correct_ps_main(sh, ctx)

    def test_missing_arg(self):
        with _base.HlslTestContext(no_file = True) as sh:
            self._generate_test_uniforms(sh)
            self._generate_add_func(sh)

            with pytest.raises(
                RuntimeError, 
                match = "Argument missing for parameter 'b'"
            ):
                sh.result.color = sh.add(a = sh.g_f4A)

    def test_extra_arg(self):
        with _base.HlslTestContext(no_file = True) as sh:
            self._generate_add_func(sh)

            with pytest.raises(
                RuntimeError,
                match = 'Uniform register b0 is already in use by cb0'
            ):
                sh.result.color = sh.add(
                    a = sh.g_f4A, b = sh.g_f4B, c = sh.g_f3C
                )

    def test_arg_type_mismatch(self):
        with _base.HlslTestContext(no_file = True) as sh:
            self._generate_add_func(sh)
            
            with pytest.raises(
                RuntimeError,
                match = 'Uniform register b0 is already in use by cb0'
            ):
                sh.result.color = sh.add(a = sh.g_f4A, b = sh.g_f3C)

    def test_void_func_decl(self):
        with _base.HlslTestContext(as_lib = True) as sh:
            sh.function('voidFuncA')(a = sh.Float4, b = sh.Float4).declare()
            sh.function('voidFuncB', type(None))(a = sh.Float4, b = sh.Float4).declare()
            sh.function('voidFuncC', None)(a = sh.Float4, b = sh.Float4).declare()

    def test_void_func_def(self):
        with _base.HlslTestContext(as_lib = True) as sh:
            with sh.function('voidFunc')(a = sh.Float4, b = sh.Float4):
                sh.c = sh.a + sh.b
                sh.return_()

    def test_func_no_args(self):
        ctx = _base.HlslTestContext()
        with ctx as sh:
            self._generate_test_uniforms(sh)

            sh.function('getA0', sh.Float4)().declare()
            sh.function('getA1', sh.Float4).declare()

            with sh.function('getA2', sh.Float4)():
                sh.return_(sh.g_f4A)

            with sh.function('getA3', sh.Float4):
                sh.return_(sh.g_f4A)

            with self._generate_ps_main(sh, ctx):
                sh.result = sh.PsOut()
                sh.result.color = sh.getA2() + sh.getA3()
                sh.return_(sh.result)
