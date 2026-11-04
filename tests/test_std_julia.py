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

"""Tests for metashade.std.procedural.julia module."""

from metashade.util.testing import ctx_cls_hg, OslTestContext
from metashade.std.procedural import julia


class TestJulia2d:
    @ctx_cls_hg
    def test_julia2d(self, ctx_cls):
        """Test julia2d generates correct code."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            sh.instantiate(julia.julia2d)

    def test_julia2d_osl(self):
        """Test julia2d on OSL, which has no builtin 2-component vector.

        julia2d only reads the ``x`` and ``y`` of its ``Float2`` texcoord,
        so a struct with those members stands in for it.
        """
        with OslTestContext(dummy_entry_point=True) as sh:
            sh.struct('Float2')(x=sh.Float, y=sh.Float)
            sh.instantiate(julia.julia2d)
