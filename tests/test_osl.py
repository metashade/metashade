# Copyright 2026 Pavlo Penenko
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
from metashade.util.testing import OslTestContext

class TestOslShader:
    def test_shader_params_rejected(self):
        with OslTestContext(no_file=True) as sh:
            with pytest.raises(NotImplementedError):
                sh.shader('main')(gain=sh.In(sh.Float, default=1.0))

class TestOslSwizzles:
    @pytest.mark.parametrize('dtype, mask', [
        ('Float3', 'xy'),
        ('Float3', 'xyz'),
        ('RgbF', 'rgb'),
    ])
    def test_mask_read_rejected(self, dtype, mask):
        with OslTestContext(no_file=True) as sh:
            with sh.function('f', sh.Float)(v=getattr(sh, dtype)):
                with pytest.raises(AttributeError):
                    getattr(sh.v, mask)
                sh.return_(sh.v.x if dtype == 'Float3' else sh.v.r)

    def test_mask_write_rejected(self):
        with OslTestContext(no_file=True) as sh:
            with sh.function('f')(v=sh.Out(sh.Float3), w=sh.Float3):
                with pytest.raises(AttributeError):
                    sh.v.xyz = sh.w
