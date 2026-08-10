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
Metashade reimplementation of the MaterialX Standard Surface nodegraph.

Phase 1: A direct ``surfaceshader``-outputting source-code override of
    ``ND_standard_surface_surfaceshader``.

    - ``TestStandardSurfacePink``: hot-pink diagnostic that validates the
      override pipeline without any BSDF logic.
    - ``TestStandardSurfaceDefault``: Diffuse + Specular implementation
      targeting ``standard_surface_default.mtlx``.  Acquires and calls
      ``mx_oren_nayar_diffuse_bsdf``, ``mx_dielectric_bsdf``, and
      ``mx_roughness_anisotropy`` from the MaterialX stdlib, then layers
      specular over diffuse inline.  ClosureData is manually injected
      into the surfaceshader-outputting function.

Phase 2 (future): A two-layer architecture with a BSDF-outputting
    source-code node (gets ``ClosureData`` injection) wired through
    a thin nodegraph to the stock ``surface`` constructor.  This will
    be needed once we start calling BSDF SCNs.
"""

from __future__ import annotations

import pytest

mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import _build_params, acquire_function
from metashade.mtlx.dtypes import register_mtlx_closure_structs
from metashade.mtlx.util.testing import GlslTestContext


_SUBDIR_PINK = "standard_surface_pink"
_SUBDIR_DIFFUSE = "standard_surface"
_SS_NODEDEF = "ND_standard_surface_surfaceshader"


def _register_surfaceshader_struct(sh):
    """Register the ``surfaceshader`` struct so Metashade can emit it."""
    sh.struct('surfaceshader', emit=False)(
        color=sh.Float3,
        transparency=sh.Float3
    )


@pytest.fixture
def ss_nodedef(stdlib_doc: mx.Document):
    """Get the default-version Standard Surface nodedef."""
    nodedef = stdlib_doc.getNodeDef(_SS_NODEDEF)
    assert nodedef is not None, f"Could not find {_SS_NODEDEF}"
    return nodedef


class TestStandardSurfacePink:
    """Pink Standard Surface: validates the override pipeline.

    Directly overrides ``ND_standard_surface_surfaceshader`` with a
    source-code function that outputs constant hot-pink.  No ClosureData
    or BSDF nodes needed -- just verifies the plumbing.
    """

    _FUNC_NAME = "mx_metashade_standard_surface_surfaceshader"

    def test_generate_pink_ss(self, ss_nodedef):
        """Generate a hot-pink Standard Surface override."""
        ctx = GlslTestContext(
            base_name=self._FUNC_NAME,
            impl_only=True,
            subdir=_SUBDIR_PINK,
        )

        with ctx as test_ctx:
            sh = test_ctx._sh

            register_mtlx_closure_structs(sh)
            _register_surfaceshader_struct(sh)

            params = _build_params(sh, ss_nodedef, self._FUNC_NAME)

            with sh.function(self._FUNC_NAME)(**params):
                sh.out_.color = [1.0, 0.0, 0.5]
                sh.out_.transparency = [0.0, 0.0, 0.0]

            test_ctx.add_node_impl(
                func_name=self._FUNC_NAME,
                mx_doc_string=(
                    "Pink diagnostic override for Standard Surface"
                ),
                nodedef_name=_SS_NODEDEF,
            )


def _find_genglsl_impl(stdlib_doc, nodedef_suffix):
    """Find the genglsl source-code implementation for a nodedef."""
    for impl in stdlib_doc.getImplementations():
        if (
            impl.getNodeDefString().endswith(nodedef_suffix)
            and impl.getTarget() == "genglsl"
        ):
            return impl
    return None


class TestStandardSurfaceDefault:
    """Diffuse + Specular Standard Surface for standard_surface_default.mtlx.

    Acquires ``mx_oren_nayar_diffuse_bsdf``, ``mx_dielectric_bsdf``, and
    ``mx_roughness_anisotropy`` from the MaterialX stdlib.  Layers
    specular over diffuse inline (the ``layer`` BSDF combiner) and maps
    the result to a ``surfaceshader`` output.

    ClosureData is manually injected as a codegen artifact (not in the
    nodedef schema) so internal BSDF calls receive proper lighting context.

    Covers Tier 1 materials: default, plastic, greysphere.
    """

    _FUNC_NAME = "mx_metashade_standard_surface_surfaceshader"

    # MaterialX GLSL enum constants (from mx_closure_type.glsl / pbrlib)
    _SCATTER_R = 0
    _DISTRIBUTION_GGX = 0

    def test_generate_default_ss(self, ss_nodedef, stdlib_doc):
        """Generate a Diffuse + Specular Standard Surface override."""
        oren_nayar_impl = _find_genglsl_impl(
            stdlib_doc, "oren_nayar_diffuse_bsdf"
        )
        dielectric_impl = _find_genglsl_impl(
            stdlib_doc, "dielectric_bsdf"
        )
        roughness_aniso_impl = _find_genglsl_impl(
            stdlib_doc, "roughness_anisotropy"
        )

        assert oren_nayar_impl is not None, (
            "Could not find genglsl impl for oren_nayar_diffuse_bsdf"
        )
        assert dielectric_impl is not None, (
            "Could not find genglsl impl for dielectric_bsdf"
        )
        assert roughness_aniso_impl is not None, (
            "Could not find genglsl impl for roughness_anisotropy"
        )

        ctx = GlslTestContext(
            base_name=self._FUNC_NAME,
            impl_only=True,
            subdir=_SUBDIR_DIFFUSE,
        )

        with ctx as test_ctx:
            sh = test_ctx._sh

            register_mtlx_closure_structs(sh)
            _register_surfaceshader_struct(sh)

            sh.include(roughness_aniso_impl.getAttribute("file"))
            sh.include(oren_nayar_impl.getAttribute("file"))
            sh.include(dielectric_impl.getAttribute("file"))

            acquire_function(sh, roughness_aniso_impl)
            acquire_function(sh, oren_nayar_impl)
            acquire_function(sh, dielectric_impl)

            params = _build_params(sh, ss_nodedef, self._FUNC_NAME)
            params = {'closureData': sh.ClosureData, **params}

            with sh.function(self._FUNC_NAME)(**params):
                # --- Roughness ---
                sh.main_roughness = sh.Float2()
                sh.mx_roughness_anisotropy(
                    roughness=sh.specular_roughness,
                    anisotropy=sh.specular_anisotropy,
                    out_=sh.main_roughness,
                )

                # --- Diffuse BSDF (Oren-Nayar) ---
                sh.diffuse_bsdf = sh.BSDF()
                sh.mx_oren_nayar_diffuse_bsdf(
                    closureData=sh.closureData,
                    weight=sh.base,
                    color=sh.base_color,
                    roughness=sh.diffuse_roughness,
                    normal=sh.normal,
                    energy_compensation=True,
                    bsdf=sh.diffuse_bsdf,
                )

                # --- Specular BSDF (dielectric reflection) ---
                sh.specular_bsdf = sh.BSDF()
                sh.mx_dielectric_bsdf(
                    closureData=sh.closureData,
                    weight=sh.specular,
                    tint=sh.specular_color,
                    ior=sh.specular_IOR,
                    roughness=sh.main_roughness,
                    retroreflective=False,
                    thinfilm_thickness=sh.thin_film_thickness,
                    thinfilm_ior=sh.thin_film_IOR,
                    normal=sh.normal,
                    tangent=sh.tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    scatter_mode=self._SCATTER_R,
                    bsdf=sh.specular_bsdf,
                )

                # --- Layer: specular over diffuse ---
                sh.out_.color = (
                    sh.specular_bsdf.response
                    + sh.diffuse_bsdf.response * sh.specular_bsdf.throughput
                )
                sh.out_.transparency = [0.0, 0.0, 0.0]

            test_ctx.add_node_impl(
                func_name=self._FUNC_NAME,
                mx_doc_string=(
                    "Metashade Standard Surface (diffuse + specular)"
                ),
                nodedef_name=_SS_NODEDEF,
            )
