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
from metashade.util.testing import ctx_cls_hg, HlslTestContext

class TestBoolType:
    """Tests for the Bool data type."""

    def _generate_uniforms(self, sh):
        with sh.uniform_buffer(
            dx_register = 0, name = 'cb',
            vk_set = 0, vk_binding = 0
        ):
            sh.uniform('g_flag', sh.Bool)
            sh.uniform('g_f4A', sh.Float4)
            sh.uniform('g_f4B', sh.Float4)

    @ctx_cls_hg
    def test_bool_in_if(self, ctx_cls):
        """Bool uniform can be used as an if_ condition."""
        ctx = ctx_cls()
        with ctx as sh:
            self._generate_uniforms(sh)

            if isinstance(ctx, HlslTestContext):
                with sh.ps_output('PsOut') as PsOut:
                    PsOut.SV_Target('color', sh.Float4)
                entry = sh.entry_point(ctx._entry_point_name, sh.PsOut)()
            else:
                sh.out_color = sh.stage_output(sh.Float4, location = 0)
                entry = sh.entry_point(ctx._entry_point_name)()

            with entry:
                if isinstance(ctx, HlslTestContext):
                    sh.result = sh.PsOut()
                    with sh.if_(sh.g_flag):
                        sh.result.color = sh.g_f4A
                    with sh.else_():
                        sh.result.color = sh.g_f4B
                    sh.return_(sh.result)
                else:
                    with sh.if_(sh.g_flag):
                        sh.out_color = sh.g_f4A
                    with sh.else_():
                        sh.out_color = sh.g_f4B

    @ctx_cls_hg
    def test_bool_function_param(self, ctx_cls):
        """Bool can be used as a function parameter annotation."""
        def _py_func(sh, flag : 'Bool', a : 'Float4', b : 'Float4') -> 'Float4':
            with sh.if_(flag):
                sh.return_(a)
            sh.return_(b)

        ctx = ctx_cls(dummy_entry_point = True)
        with ctx as sh:
            sh.instantiate(_py_func)


class TestBoolLiterals:
    """Tests for Bool literal conversion."""

    @ctx_cls_hg
    def test_bool_literal_true(self, ctx_cls):
        """Python True converts to 'true' for Bool."""
        with ctx_cls(no_file = True) as sh:
            Bool = sh.Bool._get_dtype()
            assert Bool._get_value_ref(True) == 'true'

    @ctx_cls_hg
    def test_bool_literal_false(self, ctx_cls):
        """Python False converts to 'false' for Bool."""
        with ctx_cls(no_file = True) as sh:
            Bool = sh.Bool._get_dtype()
            assert Bool._get_value_ref(False) == 'false'


class TestBoolTypeStrictness:
    """Tests that Bool rejects inappropriate operations."""

    @ctx_cls_hg
    def test_float_rejects_bool_literal(self, ctx_cls):
        """Float must reject Python bool literals."""
        with ctx_cls(no_file = True) as sh:
            Float = sh.Float._get_dtype()
            assert Float._get_value_ref(True) is None

    @ctx_cls_hg
    def test_int_rejects_bool_literal(self, ctx_cls):
        """Int must reject Python bool literals."""
        with ctx_cls(no_file = True) as sh:
            Int = sh.Int._get_dtype()
            assert Int._get_value_ref(True) is None

    @ctx_cls_hg
    def test_bool_no_arithmetic(self, ctx_cls):
        """Bool must not support arithmetic operators."""
        with ctx_cls(no_file = True) as sh:
            Bool = sh.Bool._get_dtype()
            assert not hasattr(Bool, '__add__')
            assert not hasattr(Bool, '__sub__')
            assert not hasattr(Bool, '__mul__')
            assert not hasattr(Bool, '__neg__')

    @ctx_cls_hg
    def test_bool_rejects_numeric_literal(self, ctx_cls):
        """Bool must reject numeric literals."""
        with ctx_cls(no_file = True) as sh:
            Bool = sh.Bool._get_dtype()
            assert Bool._get_value_ref(0) is None
            assert Bool._get_value_ref(1) is None
            assert Bool._get_value_ref(1.5) is None

