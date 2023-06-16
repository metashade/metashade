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

class TestSamplers(_base.Base):
    def test_combined_samplers(self):
        hlsl_path = self._get_hlsl_path('test_combined_samplers')
        with self._open_file(hlsl_path) as ps_file:
            sh = ps_6_0.Generator(ps_file)

            sh.combined_sampler_2d(
                texture_name = 'colorTexture0', texture_register = 0,
                sampler_name = 'colorSampler0', sampler_register = 1
            )
            sh.combined_sampler_2d(
                texture_name = 'colorTexture1', texture_register = 1,
                sampler_name = 'colorSampler1', sampler_register = 0,
                texel_type = sh.RgbaF
            )
            sh.combined_sampler_2d(
                texture_name = 'shadowMap', texture_register = 2,
                sampler_name = 'shadowSampler', sampler_register = 2,
                cmp = True
            )

            with sh.vs_output('VsOut') as VsOut:
                VsOut.texCoord('uv0', sh.Point2f)

            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.main(self._entry_point_name, sh.PsOut)(psIn = sh.VsOut):
                sh.psOut = sh.PsOut()
                sh.rgbaSample = sh.colorSampler1(sh.psIn.uv0)
                sh.fShadowSample0 = sh.shadowSampler(
                    sh.psIn.uv0,
                    cmp_value = sh.Float(0.5)
                )
                sh.fShadowSample1 = sh.shadowSampler(
                    sh.psIn.uv0,
                    cmp_value = sh.Float(0.1),
                    lod = 0
                )
                sh.psOut.color = \
                    sh.rgbaSample * sh.fShadowSample0 * sh.fShadowSample1
                sh.return_(sh.psOut)

        self._compile(hlsl_path, as_lib = False)
