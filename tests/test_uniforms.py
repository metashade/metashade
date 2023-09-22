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
import _base
from metashade.hlsl.sm6 import ps_6_0

class TestUniforms(_base.Base):
    def test_cb_register_clash(self):
        with self._open_file() as ps_file:
            sh = ps_6_0.Generator(ps_file)

            with sh.uniform_buffer(register = 0, name = 'cb0'):
                sh.uniform('f0', sh.Float4)

            with sh.uniform_buffer(register = 1, name = 'cb1'):
                sh.uniform('f1', sh.Float4)

            with pytest.raises(Exception):
                with sh.uniform_buffer(register = 0, name = 'cb2'):
                    sh.uniform('f2', sh.Float4)