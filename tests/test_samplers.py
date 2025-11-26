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

class TestSamplers:
    def test_combined_samplers(self):
        ctx = _base.HlslTestContext(as_lib = True)
        with ctx as sh:
            sh.uniform('g_tColor0', sh.Texture2d, dx_register = 0)
            sh.uniform('g_sColor0', sh.Sampler, dx_register = 1)

            sh.uniform('g_tColor1', sh.Texture2d(texel_type = sh.Float4), dx_register = 1)
            sh.uniform('g_sColor1', sh.Sampler, dx_register = 0)

            sh.uniform('g_tShadow', sh.Texture2d, dx_register = 2)
            sh.uniform('g_sShadow', sh.SamplerCmp, dx_register = 2)

            sh.uniform('g_t1d', sh.Texture1d, dx_register = 3)
            sh.uniform('g_t3d', sh.Texture3d, dx_register = 4)
            sh.uniform('g_tCube', sh.TextureCube, dx_register = 5)

            with sh.vs_output('VsOut') as VsOut:
                VsOut.texCoord('uv0', sh.Point2f)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.entry_point(ctx._entry_point_name, sh.PsOut)(psIn = sh.VsOut):
                sh.psOut = sh.PsOut()

                sh.rgbaSample0 = (sh.g_sColor1 @ sh.g_tColor1)(sh.psIn.uv0)

                combined_sampler = sh.g_sColor1 @ sh.g_tColor1
                sh.rgbaSample1 = combined_sampler(sh.psIn.uv0, lod = sh.Float(0.9))
                sh.rgbaSample2 = combined_sampler(sh.psIn.uv0, lod_bias = sh.Float(0.1))

                sh.fShadowSample0 = (sh.g_tShadow @ sh.g_sShadow)(
                    sh.psIn.uv0,
                    cmp_value = sh.Float(0.5)
                )
                sh.fShadowSample1 = (sh.g_sShadow @ sh.g_tShadow)(
                    sh.psIn.uv0,
                    cmp_value = sh.Float(0.1),
                    lod = 0
                )

                sh.f1dSample = (sh.g_t1d @ sh.g_sColor1)(sh.psIn.uv0.x)
                sh.f3dSample = (sh.g_sColor1 @ sh.g_t3d)(sh.Float3(0.5))
                sh.f3CubeSample = (sh.g_sColor1 @ sh.g_tCube)(sh.Float3(0.5))

                sh.psOut.color = (
                    sh.rgbaSample0 * sh.rgbaSample1 * sh.rgbaSample2 * sh.fShadowSample0 * sh.fShadowSample1
                    * sh.f1dSample * sh.f3dSample * sh.f3CubeSample
                )
                sh.return_(sh.psOut)
