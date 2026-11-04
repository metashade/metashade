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

from metashade.util.testing import (
    ctx_cls_hg, ctx_cls_hgo, HlslTestContext, GlslTestContext
)
import _auto_float_intrinsics, _auto_numeric_intrinsics

class TestIntrinsics:
    def _test(self, auto_package):
        with HlslTestContext(as_lib = True) as sh:
            with sh.uniform_buffer(dx_register = 0, name = 'cb'):
                sh.uniform('g_f', sh.Float)
                for dim in range(1, 5):
                    sh.uniform(
                        f'g_f{dim}',
                        getattr(sh, f'Float{dim}')
                    )

                for row in range(1, 5):
                    for col in range(1, 5):
                        sh.uniform(
                            f'g_f{row}x{col}',
                            getattr(sh, f'Float{row}x{col}')
                        )

            auto_package.test(sh)

    def test_float_intrinsics(self):
        self._test(_auto_float_intrinsics)

    def test_numeric_intrinsics(self):
        self._test(_auto_numeric_intrinsics)


class TestFloatIntrinsics:
    """Tests for float intrinsics across HLSL, GLSL and OSL.

    Each test validates return type and expression string for scalar
    and vector types.  New intrinsics should be added as additional
    test methods following the same pattern.  Inputs are function
    parameters because OSL has no uniforms.
    """

    def _check(self, sh, dtype, intrinsic, expected_expr):
        with sh.function('f')(v = dtype):
            result = intrinsic(sh.v)
            assert isinstance(result, dtype._get_dtype())
            assert str(result) == expected_expr

    @ctx_cls_hgo
    def test_sin_scalar(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float, lambda v: v.sin(), 'sin(v)')

    @ctx_cls_hgo
    def test_sin_vec3(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float3, lambda v: v.sin(), 'sin(v)')

    @ctx_cls_hgo
    def test_cos_scalar(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float, lambda v: v.cos(), 'cos(v)')

    @ctx_cls_hgo
    def test_cos_vec3(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float3, lambda v: v.cos(), 'cos(v)')

    @ctx_cls_hgo
    def test_radians_scalar(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float, lambda v: v.radians(), 'radians(v)')

    @ctx_cls_hgo
    def test_radians_vec3(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            self._check(sh, sh.Float3, lambda v: v.radians(), 'radians(v)')


class TestLerpReturnType:
    """lerp must return the type of the interpolated values, not the weight."""

    def _lerp(self, sh, dtype):
        with sh.function('f')(t = sh.Float, a = dtype, b = dtype):
            result = sh.t.lerp(sh.a, sh.b)
            assert isinstance(result, dtype._get_dtype())
            return str(result)

    @ctx_cls_hgo
    def test_scalar_lerp_scalar(self, ctx_cls):
        """float.lerp(float, float) returns float."""
        with ctx_cls(no_file=True) as sh:
            self._lerp(sh, sh.Float)

    @ctx_cls_hgo
    def test_scalar_lerp_vec3(self, ctx_cls):
        """float.lerp(Float3, Float3) returns Float3, not Float."""
        with ctx_cls(no_file=True) as sh:
            self._lerp(sh, sh.Float3)

    @ctx_cls_hg
    def test_scalar_lerp_vec4(self, ctx_cls):
        """float.lerp(Float4, Float4) returns Float4."""
        with ctx_cls(no_file=True) as sh:
            self._lerp(sh, sh.Float4)

    @ctx_cls_hgo
    def test_lerp_expression_string(self, ctx_cls):
        """lerp emits the correct intrinsic call."""
        with ctx_cls(no_file=True) as sh:
            result_str = self._lerp(sh, sh.Float3)
            if isinstance(ctx_cls(), HlslTestContext):
                assert result_str == 'lerp(a, b, t)'
            else:
                assert result_str == 'mix(a, b, t)'
