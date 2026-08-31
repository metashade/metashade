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
Tests for the Metashade Standard Surface implementation.

``TestStandardSurfaceDefault`` generates the BSDF source-code node and
the surfaceshader nodegraph through the test context (baseline diffing
via RefDiffer).

``TestStandardSurfacePink`` is a separate diagnostic override that
validates the surfaceshader override pipeline without any BSDF logic.
"""

from __future__ import annotations

import pytest

mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import _build_params
from metashade.mtlx.dtypes import register_mtlx_closure_structs
from metashade.mtlx.util.testing import GlslTestContext, MtlxTestContext
from metashade.mtlx import standard_surface


_SURFACESHADER_NODEDEF = "ND_standard_surface_surfaceshader"


def _register_surfaceshader_struct(sh):
    """Register the ``surfaceshader`` struct so Metashade can emit it."""
    sh.struct('surfaceshader', emit=False)(
        color=sh.Float3,
        transparency=sh.Float3
    )


@pytest.fixture
def surfaceshader_nodedef(stdlib_doc: mx.Document):
    """Get the default-version Standard Surface nodedef."""
    nodedef = stdlib_doc.getNodeDef(_SURFACESHADER_NODEDEF)
    assert nodedef is not None, f"Could not find {_SURFACESHADER_NODEDEF}"
    return nodedef


class TestStandardSurfacePink:
    """Pink Standard Surface: validates the override pipeline.

    Directly overrides ``ND_standard_surface_surfaceshader`` with a
    source-code function that outputs constant hot-pink.  No ClosureData
    or BSDF nodes needed -- just verifies the plumbing.
    """

    _FUNC_NAME = "mx_metashade_standard_surface_surfaceshader"
    _SUBDIR = "standard_surface_pink"

    def test_generate_pink_surfaceshader(self, surfaceshader_nodedef):
        """Generate a hot-pink Standard Surface override."""
        ctx = GlslTestContext(
            base_name=self._FUNC_NAME,
            impl_only=True,
            subdir=self._SUBDIR,
        )

        with ctx as test_ctx:
            sh = test_ctx._sh

            register_mtlx_closure_structs(sh)
            _register_surfaceshader_struct(sh)

            params = _build_params(sh, surfaceshader_nodedef, self._FUNC_NAME)

            with sh.function(self._FUNC_NAME)(**params):
                sh.out_.color = [1.0, 0.0, 0.5]
                sh.out_.transparency = [0.0, 0.0, 0.0]

            test_ctx.add_node_impl(
                func_name=self._FUNC_NAME,
                mx_doc_string=(
                    "Pink diagnostic override for Standard Surface"
                ),
                nodedef_name=_SURFACESHADER_NODEDEF,
            )


class TestStandardSurfaceDefault:
    """Metashade reimplementation of the Standard Surface.

    Generates the BSDF source-code node and the surfaceshader nodegraph
    together.  Both are written through the context and RefDiffer'd in CI.
    """

    def test_generate(self, stdlib_doc):
        """Generate the Standard Surface BSDF + surfaceshader nodegraph."""
        with GlslTestContext(
            base_name=standard_surface.FUNC_NAME,
            impl_only=False,
            subdir=standard_surface.SUBDIR,
        ) as glsl_ctx:
            standard_surface.generate(glsl_ctx, stdlib_doc)

        stock_nodedef = stdlib_doc.getNodeDef(
            standard_surface._SURFACESHADER_NODEDEF
        )
        ng_doc = standard_surface.generate_surfaceshader_nodegraph(
            stock_nodedef
        )

        with MtlxTestContext(
            "mx_metashade_standard_surface_nodegraph.mtlx",
            subdir=standard_surface.SUBDIR,
        ) as mtlx_ctx:
            mtlx_ctx.write(ng_doc)


class TestStandardSurfaceSubsurface0:
    """Pruned SS variant with subsurface disabled."""

    _PERM = standard_surface.Permutation(subsurface=False)

    def test_generate_bsdf(self, stdlib_doc):
        """Generate pruned SS BSDF without subsurface lobe."""
        base_name = (standard_surface._FUNC_NAME_BASE
                     + self._PERM.variant_suffix
                     + standard_surface._FUNC_NAME_TYPE)
        subdir = standard_surface.SUBDIR + self._PERM.variant_suffix

        with GlslTestContext(
            base_name=base_name,
            impl_only=False,
            subdir=subdir,
        ) as glsl_ctx:
            standard_surface.generate(glsl_ctx, stdlib_doc, perm=self._PERM)


class TestPermutation:
    """Tests for the lobe-pruning Permutation data model."""

    def test_all_lobes_enabled(self):
        """Full permutation has all lobes on and an empty suffix."""
        perm = standard_surface.Permutation()
        assert perm.subsurface is True
        assert perm.variant_suffix == ""

    def test_all_is_full_permutation(self):
        """Permutation.ALL is the full permutation."""
        assert standard_surface.Permutation.ALL == standard_surface.Permutation()
        assert standard_surface.Permutation.ALL.variant_suffix == ""

    def test_single_lobe_disabled(self):
        """Disabling one lobe produces a subtractive suffix."""
        perm = standard_surface.Permutation(subsurface=False)
        assert perm.variant_suffix == "_subsurface0"

    def test_all_lobes_disabled(self):
        """Baseline (diffuse+specular only) lists all lobes as disabled."""
        perm = standard_surface.Permutation(subsurface=False)
        suffix = perm.variant_suffix
        for lobe in standard_surface.LOBES:
            assert f"{lobe.name}0" in suffix

    def test_permutation_is_hashable(self):
        """Permutations can be used as dict keys (for caching)."""
        p1 = standard_surface.Permutation(subsurface=False)
        p2 = standard_surface.Permutation(subsurface=False)
        cache = {p1: "variant_dir"}
        assert p2 in cache

    def test_from_material_greysphere(self, stdlib_doc):
        """Greysphere has only diffuse+specular; subsurface inactive."""
        doc = mx.createDocument()
        mx.readFromXmlString(
            doc,
            """<?xml version="1.0"?>
            <materialx version="1.39">
              <standard_surface name="SR_greysphere" type="surfaceshader">
                <input name="base_color" type="color3"
                       value="0.18, 0.18, 0.18" />
                <input name="specular_roughness" type="float" value="0.7" />
              </standard_surface>
            </materialx>""",
        )

        ss_node = doc.getNode("SR_greysphere")
        assert ss_node is not None

        nodedef = stdlib_doc.getNodeDef("ND_standard_surface_surfaceshader")
        assert nodedef is not None

        perm = standard_surface.Permutation.from_material(ss_node, nodedef)
        assert perm.subsurface is False

    def test_from_material_with_subsurface(self, stdlib_doc):
        """A material with subsurface=1 should have subsurface active."""
        doc = mx.createDocument()
        mx.readFromXmlString(
            doc,
            """<?xml version="1.0"?>
            <materialx version="1.39">
              <standard_surface name="SR_jade" type="surfaceshader">
                <input name="subsurface" type="float" value="0.4" />
                <input name="subsurface_color" type="color3"
                       value="0.3, 0.6, 0.3" />
              </standard_surface>
            </materialx>""",
        )

        ss_node = doc.getNode("SR_jade")
        nodedef = stdlib_doc.getNodeDef("ND_standard_surface_surfaceshader")
        perm = standard_surface.Permutation.from_material(ss_node, nodedef)
        assert perm.subsurface is True
