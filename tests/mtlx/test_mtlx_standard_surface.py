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


class TestStandardSurface:
    """Metashade Standard Surface code generation.

    Parameterized over permutations: generates the BSDF source-code node
    and the surfaceshader nodegraph for each variant.  Both are written
    through the context and RefDiffer'd in CI.
    """

    @pytest.mark.parametrize("permutation", [
        pytest.param(standard_surface.Permutation(), id="full"),
        pytest.param(
            standard_surface.Permutation(subsurface=False), id="subsurface0",
        ),
    ])
    def test_generate(self, stdlib_doc, permutation):
        """Generate the Standard Surface BSDF + surfaceshader."""
        subdir = ("standard_surface"
                  if permutation == standard_surface.Permutation.ALL
                  else "standard_surface_pruned")

        with GlslTestContext(
            base_name=permutation.func_name,
            impl_only=False,
            subdir=subdir,
        ) as glsl_ctx:
            permutation.generate_bsdf(glsl_ctx, stdlib_doc)

        ng_doc = permutation.generate_surfaceshader_nodegraph(stdlib_doc)

        with MtlxTestContext(
            permutation.surfaceshader_filename, subdir=subdir,
        ) as mtlx_ctx:
            mtlx_ctx.write(ng_doc)
