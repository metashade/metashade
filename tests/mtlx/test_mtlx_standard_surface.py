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
Metashade reimplementation of the MaterialX Standard Surface.

Two-layer architecture:

1. A BSDF-outputting source-code node (``metashade_standard_surface_bsdf``) that
   receives ``ClosureData`` injection from the shader generator and
   calls stdlib BSDFs (Oren-Nayar diffuse, dielectric specular).

2. A thin hand-written nodegraph that wires the BSDF to the stock
   ``surface`` constructor, overriding ``ND_standard_surface_surfaceshader``.
   The nodegraph lives in ``libraries/standard_surface/`` and is loaded
   as an additional library path by the MaterialX render tests.

``TestStandardSurfacePink`` is a separate diagnostic override that
validates the surfaceshader override pipeline without any BSDF logic.
"""

from __future__ import annotations

import pytest

mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import _build_params, acquire_function
from metashade.mtlx.dtypes import (
    mtlx_to_metashade_dtype,
    register_mtlx_closure_structs,
)
from metashade.mtlx.util.testing import GlslTestContext


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


def _find_genglsl_impl(stdlib_doc, nodedef_suffix):
    """Find the genglsl source-code implementation for a nodedef."""
    for impl in stdlib_doc.getImplementations():
        if (
            impl.getNodeDefString().endswith(nodedef_suffix)
            and impl.getTarget() == "genglsl"
        ):
            return impl
    return None


_BSDF_INPUTS = frozenset({
    "base", "base_color", "diffuse_roughness",
    "metalness",
    "specular", "specular_color", "specular_roughness",
    "specular_IOR", "specular_anisotropy",
    "thin_film_thickness", "thin_film_IOR",
    "normal", "tangent",
})


def _build_bsdf_params(sh, surfaceshader_nodedef):
    """Build BSDF node params from a subset of the surfaceshader nodedef inputs.

    Types are derived from the surfaceshader nodedef so that
    ``color3`` vs ``vector3`` distinctions are preserved in the
    generated BSDF nodedef.  ``closureData`` is placed first (skipped
    from the nodedef by ``add_node_impl``) and the BSDF output is last.
    """
    params = {"closureData": sh.ClosureData}

    for inp in surfaceshader_nodedef.getActiveInputs():
        name = inp.getName()
        if name not in _BSDF_INPUTS:
            continue
        dtype = mtlx_to_metashade_dtype(inp.getType(), sh)
        assert dtype is not None, (
            f"Unmappable type for {name}: {inp.getType()}"
        )
        params[name] = dtype

    params["bsdf"] = sh.InOut(sh.BSDF)
    return params


class TestStandardSurfaceDefault:
    """Metashade reimplementation of the Standard Surface BSDF.

    Generates ``metashade_standard_surface_bsdf``, a source-code node
    that acquires stdlib BSDFs and progressively rebuilds the
    Standard Surface shading model.  ``closureData`` is injected by
    the shader generator; a thin hand-written nodegraph wires this
    BSDF to the stock ``surface`` constructor, overriding
    ``ND_standard_surface_surfaceshader``.
    """

    _FUNC_NAME = "mx_metashade_standard_surface_bsdf"
    _SUBDIR = "standard_surface"

    # MaterialX GLSL enum constants (from mx_closure_type.glsl / pbrlib)
    _SCATTER_R = 0
    _DISTRIBUTION_GGX = 0

    def test_generate_bsdf(self, surfaceshader_nodedef, stdlib_doc):
        """Generate a diffuse + specular + conductor BSDF source-code node."""
        oren_nayar_impl = _find_genglsl_impl(
            stdlib_doc, "oren_nayar_diffuse_bsdf"
        )
        dielectric_impl = _find_genglsl_impl(
            stdlib_doc, "dielectric_bsdf"
        )
        conductor_impl = _find_genglsl_impl(
            stdlib_doc, "conductor_bsdf"
        )
        artistic_ior_impl = _find_genglsl_impl(
            stdlib_doc, "artistic_ior"
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
        assert conductor_impl is not None, (
            "Could not find genglsl impl for conductor_bsdf"
        )
        assert artistic_ior_impl is not None, (
            "Could not find genglsl impl for artistic_ior"
        )
        assert roughness_aniso_impl is not None, (
            "Could not find genglsl impl for roughness_anisotropy"
        )

        ctx = GlslTestContext(
            base_name=self._FUNC_NAME,
            impl_only=False,
            subdir=self._SUBDIR,
        )

        with ctx as test_ctx:
            sh = test_ctx._sh

            register_mtlx_closure_structs(sh)

            sh.include(roughness_aniso_impl.getAttribute("file"))
            sh.include(oren_nayar_impl.getAttribute("file"))
            sh.include(dielectric_impl.getAttribute("file"))
            sh.include(conductor_impl.getAttribute("file"))
            sh.include(artistic_ior_impl.getAttribute("file"))

            acquire_function(sh, roughness_aniso_impl)
            acquire_function(sh, oren_nayar_impl)
            acquire_function(sh, dielectric_impl)
            acquire_function(sh, conductor_impl)
            acquire_function(sh, artistic_ior_impl)

            params = _build_bsdf_params(sh, surfaceshader_nodedef)

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
                sh.diffuse_bsdf.response = [0.0, 0.0, 0.0]
                sh.diffuse_bsdf.throughput = [1.0, 1.0, 1.0]
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
                sh.specular_bsdf.response = [0.0, 0.0, 0.0]
                sh.specular_bsdf.throughput = [1.0, 1.0, 1.0]
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
                sh.bsdf.response = (
                    sh.specular_bsdf.response
                    + sh.diffuse_bsdf.response * sh.specular_bsdf.throughput
                )
                sh.bsdf.throughput = (
                    sh.specular_bsdf.throughput * sh.diffuse_bsdf.throughput
                )

                # --- Artistic IOR (reflectivity/edge-color -> physical IOR/extinction) ---
                sh.metal_reflectivity = sh.base_color * sh.base
                sh.metal_edgecolor = sh.specular_color * sh.specular
                sh.ior_n = sh.RgbF()
                sh.ior_k = sh.RgbF()
                sh.mx_artistic_ior(
                    reflectivity=sh.metal_reflectivity,
                    edge_color=sh.metal_edgecolor,
                    ior=sh.ior_n,
                    extinction=sh.ior_k,
                )

                # --- Conductor BSDF (metal reflection) ---
                sh.metal_bsdf = sh.BSDF()
                sh.metal_bsdf.response = [0.0, 0.0, 0.0]
                sh.metal_bsdf.throughput = [1.0, 1.0, 1.0]
                sh.mx_conductor_bsdf(
                    closureData=sh.closureData,
                    weight=1.0,
                    ior=sh.ior_n,
                    extinction=sh.ior_k,
                    roughness=sh.main_roughness,
                    retroreflective=False,
                    thinfilm_thickness=sh.thin_film_thickness,
                    thinfilm_ior=sh.thin_film_IOR,
                    normal=sh.normal,
                    tangent=sh.tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    bsdf=sh.metal_bsdf,
                )

                # --- Metalness mix: conductor (fg) vs specular+diffuse (bg) ---
                sh.one_minus_metalness = sh.Float(1) - sh.metalness
                sh.bsdf.response = (
                    sh.metal_bsdf.response * sh.metalness
                    + sh.bsdf.response * sh.one_minus_metalness
                )
                sh.bsdf.throughput = (
                    sh.metal_bsdf.throughput * sh.metalness
                    + sh.bsdf.throughput * sh.one_minus_metalness
                )

            test_ctx.add_node_impl(
                func_name=self._FUNC_NAME,
                mx_doc_string=(
                    "Metashade Standard Surface BSDF "
                    "(diffuse + specular + conductor)"
                ),
            )
