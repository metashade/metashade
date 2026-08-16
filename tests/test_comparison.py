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

import pytest
from metashade.util.testing import ctx_cls_hg, HlslTestContext, GlslTestContext


class TestComparisonOperators:
    """Tests for comparison operators on ArithmeticType."""

    @ctx_cls_hg
    def test_gt_returns_bool(self, ctx_cls):
        """Greater-than produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x > 0.0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x > 0.0'

    @ctx_cls_hg
    def test_lt_returns_bool(self, ctx_cls):
        """Less-than produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x < 1.0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x < 1.0'

    @ctx_cls_hg
    def test_ge_returns_bool(self, ctx_cls):
        """Greater-or-equal produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x >= 0.5
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x >= 0.5'

    @ctx_cls_hg
    def test_le_returns_bool(self, ctx_cls):
        """Less-or-equal produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x <= 2.0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x <= 2.0'

    @ctx_cls_hg
    def test_eq_returns_bool(self, ctx_cls):
        """Equality produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x == 0.0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x == 0.0'

    @ctx_cls_hg
    def test_ne_returns_bool(self, ctx_cls):
        """Not-equal produces a Bool expression."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            result = sh.g_x != 0.0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_x != 0.0'


class TestComparisonWithArithmeticSubexpressions:
    """Compound arithmetic subexpressions are parenthesized in comparisons."""

    @ctx_cls_hg
    def test_compound_lhs_parenthesized(self, ctx_cls):
        """Arithmetic expression on LHS gets parenthesized."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_a', sh.Float)
            sh.uniform('g_b', sh.Float)
            result = (sh.g_a + sh.g_b) > 1.0
            assert str(result) == '(g_a + g_b) > 1.0'

    @ctx_cls_hg
    def test_simple_lhs_not_parenthesized(self, ctx_cls):
        """Simple variable on LHS is not parenthesized."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_a', sh.Float)
            result = sh.g_a > 0.0
            assert str(result) == 'g_a > 0.0'


class TestComparisonInIf:
    """Comparison results can be used directly in sh.if_()."""

    def _generate_uniforms(self, sh):
        with sh.uniform_buffer(
            dx_register=0, name='cb',
            vk_set=0, vk_binding=0
        ):
            sh.uniform('g_x', sh.Float)
            sh.uniform('g_f4A', sh.Float4)
            sh.uniform('g_f4B', sh.Float4)

    @ctx_cls_hg
    def test_comparison_in_if(self, ctx_cls):
        """A comparison result can drive an if_/else_ block."""
        ctx = ctx_cls()
        with ctx as sh:
            self._generate_uniforms(sh)

            if isinstance(ctx, HlslTestContext):
                with sh.ps_output('PsOut') as PsOut:
                    PsOut.SV_Target('color', sh.Float4)
                entry = sh.entry_point(ctx._entry_point_name, sh.PsOut)()
            else:
                sh.out_color = sh.stage_output(sh.Float4, location=0)
                entry = sh.entry_point(ctx._entry_point_name)()

            with entry:
                if isinstance(ctx, HlslTestContext):
                    sh.result = sh.PsOut()
                    with sh.if_(sh.g_x > 0.0):
                        sh.result.color = sh.g_f4A
                    with sh.else_():
                        sh.result.color = sh.g_f4B
                    sh.return_(sh.result)
                else:
                    with sh.if_(sh.g_x > 0.0):
                        sh.out_color = sh.g_f4A
                    with sh.else_():
                        sh.out_color = sh.g_f4B


class TestComparisonIntOperands:
    """Comparison operators work on Int types too."""

    @ctx_cls_hg
    def test_int_gt(self, ctx_cls):
        """Int > int literal produces a Bool."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_i', sh.Int)
            result = sh.g_i > 0
            assert isinstance(result, sh.Bool._get_dtype())
            assert str(result) == 'g_i > 0'


class TestComparisonTypeRejection:
    """Comparisons reject incompatible operands."""

    @ctx_cls_hg
    def test_gt_rejects_string(self, ctx_cls):
        """Comparison with a string raises TypeError."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            with pytest.raises(TypeError):
                sh.g_x > "hello"

    @ctx_cls_hg
    def test_eq_rejects_string(self, ctx_cls):
        """Equality with a string falls back to identity (False)."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            assert (sh.g_x == "hello") is False

    @ctx_cls_hg
    def test_gt_rejects_bool(self, ctx_cls):
        """Comparison with a Python bool raises TypeError."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            with pytest.raises(TypeError):
                sh.g_x > True

    @ctx_cls_hg
    def test_eq_rejects_bool(self, ctx_cls):
        """Equality with a Python bool raises TypeError."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            with pytest.raises(TypeError):
                sh.g_x == True


class TestComparisonHashability:
    """Float and Int remain hashable after adding __eq__."""

    @ctx_cls_hg
    def test_hashable(self, ctx_cls):
        """Instances can be used in sets and as dict keys."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_x', sh.Float)
            sh.uniform('g_y', sh.Float)
            s = {sh.g_x, sh.g_y}
            assert sh.g_x in s
            d = {sh.g_x: 'a'}
            assert d[sh.g_x] == 'a'


class TestVectorComparisonAbsent:
    """Vector types must not inherit scalar comparison operators."""

    @ctx_cls_hg
    def test_float3_no_gt(self, ctx_cls):
        """Float3 must not support > (would need bvec3 return type)."""
        with ctx_cls(no_file=True) as sh:
            sh.uniform('g_v', sh.Float3)
            with pytest.raises(TypeError):
                sh.g_v > 0.0
