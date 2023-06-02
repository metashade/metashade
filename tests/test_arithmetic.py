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

import pytest, _base
from metashade.hlsl.sm6 import ps_6_0

class TestArithmetic(_base.Base):
    def test_arithmetic(self):
        hlsl_path = self._get_hlsl_path('test_arithmetic')
        with self._open_file(hlsl_path) as ps_file:
            sh = ps_6_0.Generator(ps_file)
            
            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', sh.Float4)

            with sh.function('test_arithmetic', sh.Float2)():
                sh.fD = sh.Float(-1)

                sh.f2A = sh.Float2(0)
                sh.f2B = sh.Float2(1)
                
                sh.f2C = sh.f2A + sh.f2B
                sh.f2C += sh.f2B
                
                sh.f2C = sh.f2A - sh.f2B
                sh.f2C -= sh.f2B

                sh.f2C = sh.f2A * sh.f2B
                sh.f2C *= sh.f2B

                sh.f2C = sh.f2A / sh.f2B
                sh.f2C /= sh.f2B

                sh.f2C = sh.f2A * sh.fD
                sh.f2C *= sh.fD

                sh.f2C = sh.f2A / sh.fD
                sh.f2C /= sh.fD
                sh.return_(sh.f2C)

        self._compile(hlsl_path, as_lib = True)
