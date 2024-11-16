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

import _base
from metashade.glsl import fs

class TestGlslSimpleFs(_base.Base):
    def test_glsl_simple_fs(self):
        glsl_path = self._get_glsl_path('test_glsl_simple_fs')

        with self._open_file(glsl_path) as fs_file:
            sh = fs.Generator(fs_file, '450')

            sh.f4OutColor = sh.out(sh.Float4, location=0)

            with sh.main(self._entry_point_name)():
                sh.f4OutColor = sh.Float4(1.0, 0.0, 0.0, 1.0)

        self._check_source(glsl_path)