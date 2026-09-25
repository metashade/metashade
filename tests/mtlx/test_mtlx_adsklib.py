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

"""
Tests for pruning ``standard_surface`` nodes inside Autodesk library
nodegraphs (``adsk:metal``, ``adsk:opaque``, etc.).

These tests are conditional: they are skipped when running against
upstream ASWF MaterialX, which does not include the ``adsklib``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

mx = pytest.importorskip("MaterialX")

from metashade.mtlx.util.testing import MtlxTestContext
from metashade.mtlx import standard_surface

# Locate adsklib relative to the metashade submodule inside MaterialX:
# tests/mtlx/ -> tests/ -> metashade/ -> contrib/ -> contrib/adsk/libraries/adsklib
_ADSKLIB_DIR = (
    Path(__file__).parent.parent.parent.parent
    / "adsk" / "libraries" / "adsklib"
)
_ADSKLIB_NG = _ADSKLIB_DIR / "adsklib_ng.mtlx"

_SUBDIR = "adsklib_pruned"

pytestmark = pytest.mark.skipif(
    not _ADSKLIB_NG.exists(),
    reason="adsklib not available (upstream MaterialX)",
)


class TestAdsklibPruning:
    """Prune ``standard_surface`` inside adsk wrapper nodegraphs."""

    def test_prune_adsklib(self, aswf_lib_doc):
        """Prune adsklib_ng.mtlx and write as a reviewable reference."""
        lib_doc = mx.createDocument()
        lib_doc.importLibrary(aswf_lib_doc)
        mx.readFromXmlFile(lib_doc, str(_ADSKLIB_NG))

        pruned = standard_surface.prune_library(aswf_lib_doc, lib_doc)
        assert pruned, "Expected at least one standard_surface node to be pruned"

        # Extract just the pruned nodegraphs (strip the imported ASWF libs)
        out_doc = mx.createDocument()
        mx.readFromXmlFile(out_doc, str(_ADSKLIB_NG))
        standard_surface.prune_library(aswf_lib_doc, out_doc)

        with MtlxTestContext("adsklib_ng_pruned.mtlx", subdir=_SUBDIR) as ctx:
            ctx.write(out_doc)
