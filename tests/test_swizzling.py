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

import pytest
from metashade.util.testing import ctx_cls_hg

class TestSwizzling:
    @ctx_cls_hg
    def test_rgba_swizzling(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('rgba_swizzle', sh.Float)(
                rgb = sh.RgbF, rgba = sh.RgbaF
            ):
                sh.r = sh.rgb.r
                sh.g = sh.rgba.g
                sh.rgba.rb = sh.rgba.rg
                sh.return_(sh.r + sh.g)

    @ctx_cls_hg
    def test_xyzw_swizzling(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('xyzw_swizzle', sh.Float)(
                f3In = sh.Float3, f4In = sh.Float4
            ):
                sh.x = sh.f3In.x
                sh.yz = sh.f3In.yz
                
                sh.f3 = sh.Float3()
                sh.f3.z = sh.Float(1)
                sh.f3.xy = sh.yz

                sh.w = sh.f4In.w
                sh.f4 = sh.f4In.yyzz

                sh.f4.xy = sh.yz
                sh.return_(sh.x)

    @ctx_cls_hg
    def test_expression_swizzling(self, ctx_cls):
        """Test swizzling on arithmetic expressions."""
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('expr_swizzle', sh.Float)(
                v1 = sh.Float4, v2 = sh.Float4
            ):
                # (v1 + v2).x -> Should ensure (v1 + v2) is wrapped
                sh.res1 = (sh.v1 + sh.v2).x

                # ((v1 * v2) + v1).w
                sh.res2 = ((sh.v1 * sh.v2) + sh.v1).w

                sh.return_(sh.res1 + sh.res2)

    @ctx_cls_hg
    def test_rgba_rgb_augmented(self, ctx_cls):
        """Test augmented assignment on rgba.rgb swizzle (_is_lvalue propagation)."""
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('rgba_rgb_augmented', sh.RgbaF)(
                rgba = sh.RgbaF, rgb = sh.RgbF
            ):
                # This requires _is_lvalue to be propagated from rgba to rgba.rgb
                sh.rgba.rgb += sh.rgb
                sh.return_(sh.rgba)
