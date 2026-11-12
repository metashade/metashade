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

"""Tests for metashade.std.procedural.noisy_squares module."""

from metashade.util.testing import ctx_cls_hg
from metashade.std.procedural import noisy_squares


class TestNoisySquares2d:
    # Not on OSL: OSL has no Float2 of its own, only MaterialX's vector2, so
    # tests/mtlx/test_mtlx_noisy_squares2d.py covers OSL.
    @ctx_cls_hg
    def test_std_procedural_noisy_squares_noisy_squares2d(self, ctx_cls):
        """Test noisy_squares2d generates correct code."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            sh.instantiate(noisy_squares.noisy_squares2d)
