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
from metashade.hlsl.sm6 import ps_6_0

class TestSwizzling(_base.TestBase):
    def test_rgba_swizzling(self):
        with _base.HlslTestContext(as_lib = True) as ctx:
            with ctx.open_file() as ps_file:
                sh = ps_6_0.Generator(ps_file)

                with sh.function('rgba_swizzle', sh.Float)(
                    rgb = sh.RgbF, rgba = sh.RgbaF
                ):
                    sh.r = sh.rgb.r
                    sh.g = sh.rgba.g
                    sh.rgba.rb = sh.rgba.rg
                    sh.return_(sh.r + sh.g)

    def test_xyzw_swizzling(self):
        with _base.HlslTestContext(as_lib = True) as ctx:
            with ctx.open_file() as ps_file:
                sh = ps_6_0.Generator(ps_file)

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
