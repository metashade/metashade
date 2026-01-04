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

"""Tests for metashade.std.surf.pbr.fresnel module."""

from metashade.util.testing import ctx_cls_hg
from metashade.std.surf.pbr import fresnel


class TestFSchlick:
    @ctx_cls_hg
    def test_F_Schlick(self, ctx_cls):
        """Test F_Schlick generates correct code."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            sh.instantiate(fresnel.F_Schlick)
