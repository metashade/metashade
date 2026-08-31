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

``TestStandardSurfaceDefault`` is a thin wrapper around
:func:`metashade.mtlx.standard_surface.generate` that runs the BSDF
codegen through the test context (baseline diffing).

``TestStandardSurfacePink`` is a separate diagnostic override that
validates the surfaceshader override pipeline without any BSDF logic.

``TestSurfaceshaderNodegraph`` verifies that
:func:`metashade.mtlx.standard_surface.generate_surfaceshader_nodegraph`
produces a nodegraph structurally identical to the hand-written library
file.
"""

from __future__ import annotations
import os

import pytest

mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import _build_params
from metashade.mtlx.dtypes import register_mtlx_closure_structs
from metashade.mtlx.util.testing import GlslTestContext
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
    """Metashade reimplementation of the Standard Surface BSDF.

    Thin wrapper that delegates to
    :func:`metashade.mtlx.standard_surface.generate`.
    """

    def test_generate_bsdf(self, stdlib_doc):
        """Generate the Standard Surface BSDF source-code node."""
        ctx = GlslTestContext(
            base_name=standard_surface.FUNC_NAME,
            impl_only=False,
            subdir=standard_surface.SUBDIR,
        )

        with ctx as test_ctx:
            standard_surface.generate(test_ctx, stdlib_doc)


class TestSurfaceshaderNodegraph:
    """Verify programmatic surfaceshader nodegraph generation.

    Generates the nodegraph with PyMaterialX and writes it to the ref
    directory.  The test then loads the hand-written library file and
    compares the two documents node-by-node.
    """

    _REF_PATH = (
        standard_surface.MTLX_LIBRARIES_DIR
        / "standard_surface"
        / "mx_metashade_standard_surface_surfaceshader.mtlx"
    )

    def test_generate_matches_handwritten(self, stdlib_doc):
        """Generated nodegraph matches the hand-written library file."""
        ss_nodedef = stdlib_doc.getNodeDef(
            standard_surface._SURFACESHADER_NODEDEF
        )
        doc = standard_surface.generate_surfaceshader_nodegraph(ss_nodedef)

        out_dir = GlslTestContext._out_dir_root / standard_surface.SUBDIR
        os.makedirs(out_dir, exist_ok=True)
        out_path = out_dir / "mx_metashade_standard_surface_nodegraph.mtlx"
        mx.writeToXmlFile(doc, str(out_path))

        ref_doc = mx.createDocument()
        mx.readFromXmlFile(ref_doc, str(self._REF_PATH))

        gen_ng = doc.getNodeGraph(standard_surface._NODEGRAPH_NAME)
        ref_ng = ref_doc.getNodeGraph(standard_surface._NODEGRAPH_NAME)
        assert gen_ng is not None, "Generated nodegraph missing"
        assert ref_ng is not None, "Reference nodegraph missing"

        assert (
            gen_ng.getNodeDefString() == ref_ng.getNodeDefString()
        ), "Nodegraph nodedef mismatch"

        gen_children = {c.getName(): c for c in gen_ng.getChildren()}
        ref_children = {c.getName(): c for c in ref_ng.getChildren()}
        assert gen_children.keys() == ref_children.keys(), (
            f"Child name mismatch.\n"
            f"  Generated: {sorted(gen_children.keys())}\n"
            f"  Reference: {sorted(ref_children.keys())}"
        )

        for name in ref_children:
            gen_child = gen_children[name]
            ref_child = ref_children[name]
            assert gen_child.getCategory() == ref_child.getCategory(), (
                f"Category mismatch for '{name}': "
                f"{gen_child.getCategory()} != {ref_child.getCategory()}"
            )

            if not hasattr(ref_child, "getActiveInputs"):
                assert gen_child.getType() == ref_child.getType(), (
                    f"Output type mismatch for '{name}'"
                )
                assert (
                    gen_child.getNodeName() == ref_child.getNodeName()
                ), f"Output node connection mismatch for '{name}'"
                continue

            gen_inputs = {
                i.getName(): i for i in gen_child.getActiveInputs()
            }
            ref_inputs = {
                i.getName(): i for i in ref_child.getActiveInputs()
            }
            assert gen_inputs.keys() == ref_inputs.keys(), (
                f"Input name mismatch for '{name}'.\n"
                f"  Generated: {sorted(gen_inputs.keys())}\n"
                f"  Reference: {sorted(ref_inputs.keys())}"
            )

            for inp_name in ref_inputs:
                gen_inp = gen_inputs[inp_name]
                ref_inp = ref_inputs[inp_name]
                assert gen_inp.getType() == ref_inp.getType(), (
                    f"Type mismatch: {name}/{inp_name}"
                )
                assert (
                    gen_inp.getInterfaceName()
                    == ref_inp.getInterfaceName()
                ), f"Interface mismatch: {name}/{inp_name}"
                assert (
                    gen_inp.getNodeName() == ref_inp.getNodeName()
                ), f"Node connection mismatch: {name}/{inp_name}"
                assert (
                    gen_inp.getValueString()
                    == ref_inp.getValueString()
                ), f"Value mismatch: {name}/{inp_name}"
