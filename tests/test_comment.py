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

class TestComment(_base.TestBase):
    def test_comment(self):
        with _base.HlslTestContext('test_comment', as_lib = True) as ctx:
            with ctx.open_file() as ps_file:
                sh = ps_6_0.Generator(ps_file)

                sh // "This is a comment documenting the function"
                sh // ""
                with sh.function(
                    'test_comment', sh.Float
                )():
                    sh.fA = sh.Float(-1)
                    sh.fB = sh.Float(0)
                    sh // "fC is the sum of fA and fB"
                    sh.fC = sh.fA + sh.fB
                    sh.return_(sh.fC)
