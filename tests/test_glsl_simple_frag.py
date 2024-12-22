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

import os
import _base
from metashade.glsl import frag

class TestGlslSimpleFrag(_base.TestBase):
    def test_glsl_simple_frag(self):
        with _base.GlslTestContext(
            'test_glsl_simple_frag'
        ) as ctx:
            with ctx.open_file() as fs_file:
                sh = frag.Generator(fs_file, '450')

                sh.f4OutColor = sh.out(sh.Float4, location=0)

                with sh.entry_point('main')():
                    sh.f4OutColor = sh.Float4((1.0, 0.0, 0.0, 1.0))
