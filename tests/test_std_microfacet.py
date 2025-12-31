# Copyright 2025 Pavlo Penenko
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

"""Tests for metashade.std.surf.pbr.microfacet module.

Note: These tests are HLSL-only because the microfacet functions use
intrinsics (saturate, sqrt) not yet implemented for GLSL.
"""

from metashade.util.testing import HlslTestContext
from metashade.std.surf.pbr import microfacet


class TestDGgx:
    def test_D_Ggx(self):
        """Test D_Ggx generates correct code."""
        ctx = HlslTestContext(dummy_entry_point=True)
        with ctx as sh:
            sh.instantiate(microfacet.D_Ggx)


class TestVSmithGgxCorrelated:
    def test_V_SmithGgxCorrelated(self):
        """Test V_SmithGgxCorrelated generates correct code."""
        ctx = HlslTestContext(dummy_entry_point=True)
        with ctx as sh:
            sh.instantiate(microfacet.V_SmithGgxCorrelated)
