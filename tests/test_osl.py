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
