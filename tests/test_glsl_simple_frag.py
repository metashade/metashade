# Copyright 2024 Pavlo Penenko
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
import _base

class TestGlslSimpleFrag(_base.TestBase):
    def test_glsl_simple_frag(self):
        with _base.GlslTestContext() as sh:
            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)

            with sh.entry_point('main')():
                sh.out_f4Color = sh.Float4((1.0, 0.0, 0.0, 1.0))

    def test_glsl_inout(self):
        with _base.GlslTestContext() as sh:
            sh.in_f4Color = sh.stage_input(sh.Float4, location = 0)
            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)

            with sh.entry_point('main')():
                sh.out_f4Color = sh.in_f4Color

    def test_glsl_input_clash(self):
        with _base.GlslTestContext(no_file = True) as sh:
            sh.in_f4_0 = sh.stage_input(sh.Float4, location = 0)
            sh.out_f4 = sh.stage_output(sh.Float4, location = 0)

            sh.in_f4_1 = sh.stage_input(sh.Float4, location = 1)
            
            with pytest.raises(
                RuntimeError,
                match = 'Uniform register b0 is already in use by cb0'
            ):
                sh.in_f4_2 = sh.stage_input(sh.Float4, location = 0)

    def test_glsl_output_clash(self):
        with _base.GlslTestContext(no_file = True) as sh:
            sh.in_f4 = sh.stage_input(sh.Float4, location = 0)
            sh.out_f4_0 = sh.stage_output(sh.Float4, location = 0)

            sh.out_f4_1 = sh.stage_output(sh.Float4, location = 1)
            
            with pytest.raises(
                RuntimeError,
                match = 'Uniform register b0 is already in use by cb0'
            ):
                sh.out_f4_2 = sh.stage_output(sh.Float4, location = 0)
