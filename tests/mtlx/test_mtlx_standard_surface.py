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


def _find_genglsl_impl(stdlib_doc, node_name):
    """Find the genglsl source-code implementation for a node."""
    for impl in stdlib_doc.getImplementations():
        if (
            impl.getNodeDefString().endswith(node_name)
            and impl.getTarget() == "genglsl"
        ):
            return impl
    return None


def _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, node_names):
    """Resolve, include, and acquire stdlib sourcecode nodes.

    *node_names* is an ordered sequence of MaterialX source-code node
    names whose genglsl implementations will be included and acquired.
    Order matters: dependencies must come before dependents so that
    ``#include`` directives are emitted in the right order.
    """
    for name in node_names:
        impl = _find_genglsl_impl(stdlib_doc, name)
        assert impl is not None, (
            f"Could not find genglsl impl for {name}"
        )
        sh.include(impl.getAttribute("file"))
        acquire_function(sh, impl)


_BSDF_INPUTS = frozenset({
    "base", "base_color", "diffuse_roughness",
    "metalness",
    "specular", "specular_color", "specular_roughness",
    "specular_IOR", "specular_anisotropy", "specular_rotation",
    "sheen", "sheen_color", "sheen_roughness",
    "coat", "coat_color", "coat_roughness", "coat_anisotropy",
    "coat_rotation", "coat_IOR", "coat_normal",
    "coat_affect_color", "coat_affect_roughness",
    "subsurface", "subsurface_color", "subsurface_radius",
    "subsurface_scale", "subsurface_anisotropy",
    "thin_walled",
    "transmission", "transmission_color", "transmission_extra_roughness",
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
    _SCATTER_T = 1
    _DISTRIBUTION_GGX = 0

    _STDLIB_IMPORTS = (
        "roughness_anisotropy",
        "rotate3d_vector3",
        "oren_nayar_diffuse_bsdf",
        "translucent_bsdf",
        "subsurface_bsdf",
        "sheen_bsdf",
        "dielectric_bsdf",
        "conductor_bsdf",
        "artistic_ior",
    )

    def test_generate_bsdf(self, surfaceshader_nodedef, stdlib_doc):
        """Generate the Standard Surface BSDF source-code node."""
        ctx = GlslTestContext(
            base_name=self._FUNC_NAME,
            impl_only=False,
            subdir=self._SUBDIR,
        )

        with ctx as test_ctx:
            sh = test_ctx._sh

            register_mtlx_closure_structs(sh)
            _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, self._STDLIB_IMPORTS)

            params = _build_bsdf_params(sh, surfaceshader_nodedef)

            with sh.function(self._FUNC_NAME)(**params):
                sh // ""
                sh // "Coat affect roughness: blend specular roughness toward 1.0"
                sh.coat_roughness_factor = (
                    sh.coat_affect_roughness * sh.coat * sh.coat_roughness
                )
                sh.coat_affected_specular_roughness = (
                    sh.specular_roughness * (sh.Float(1) - sh.coat_roughness_factor)
                    + sh.coat_roughness_factor
                )

                sh // ""
                sh // "Roughness"
                sh.main_roughness = sh.Float2()
                sh.mx_roughness_anisotropy(
                    roughness=sh.coat_affected_specular_roughness,
                    anisotropy=sh.specular_anisotropy,
                    out_=sh.main_roughness,
                )

                sh // ""
                sh // "Tangent rotation"
                sh.main_tangent = sh.tangent
                with sh.if_(sh.specular_anisotropy > 0.0):
                    sh.tangent_rotate_degree = sh.specular_rotation * 360.0
                    sh.tangent_rotated = sh.Float3()
                    sh.mx_rotate_vector3(
                        in_=sh.tangent,
                        amount=sh.tangent_rotate_degree,
                        axis=sh.normal,
                        out_=sh.tangent_rotated,
                    )
                    sh.main_tangent = sh.tangent_rotated.normalize()

                sh // ""
                sh // "Coat tangent rotation"
                sh.coat_tangent = sh.tangent
                with sh.if_(sh.coat_anisotropy > 0.0):
                    sh.coat_tangent_rotate_degree = sh.coat_rotation * 360.0
                    sh.coat_tangent_rotated = sh.Float3()
                    sh.mx_rotate_vector3(
                        in_=sh.tangent,
                        amount=sh.coat_tangent_rotate_degree,
                        axis=sh.coat_normal,
                        out_=sh.coat_tangent_rotated,
                    )
                    sh.coat_tangent = sh.coat_tangent_rotated.normalize()

                sh // ""
                sh // "Coat affect color: darken diffuse under the coat"
                # RgbF workaround: exponent is unitless, not a color (#224)
                sh.coat_gamma = sh.RgbF(
                    sh.coat.clamp(0.0, 1.0) * sh.coat_affect_color + 1.0
                )
                sh.coat_affected_diffuse_color = (
                    sh.base_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
                )

                sh // ""
                sh // "Coat affect subsurface color"
                # RgbF workaround: exponent is unitless, not a color (#224)
                sh.coat_affected_subsurface_color = (
                    sh.subsurface_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
                )

                sh // ""
                sh // "Diffuse BSDF (Oren-Nayar)"
                sh.diffuse_bsdf = sh.BSDF()
                sh.diffuse_bsdf.response = [0.0, 0.0, 0.0]
                sh.diffuse_bsdf.throughput = [1.0, 1.0, 1.0]
                sh.mx_oren_nayar_diffuse_bsdf(
                    closureData=sh.closureData,
                    weight=sh.base,
                    color=sh.coat_affected_diffuse_color,
                    roughness=sh.diffuse_roughness,
                    normal=sh.normal,
                    energy_compensation=True,
                    bsdf=sh.diffuse_bsdf,
                )

                sh // ""
                sh // "Subsurface scattering"
                sh.subsurface_radius_scaled = sh.subsurface_radius * sh.subsurface_scale
                sh.sss_bsdf = sh.BSDF()
                sh.sss_bsdf.response = [0.0, 0.0, 0.0]
                sh.sss_bsdf.throughput = [1.0, 1.0, 1.0]
                with sh.if_(sh.thin_walled):
                    sh.mx_translucent_bsdf(
                        closureData=sh.closureData,
                        weight=1.0,
                        color=sh.coat_affected_subsurface_color,
                        normal=sh.normal,
                        bsdf=sh.sss_bsdf,
                    )
                with sh.else_():
                    sh.mx_subsurface_bsdf(
                        closureData=sh.closureData,
                        weight=1.0,
                        color=sh.coat_affected_subsurface_color,
                        radius=sh.subsurface_radius_scaled,
                        anisotropy=sh.subsurface_anisotropy,
                        normal=sh.normal,
                        bsdf=sh.sss_bsdf,
                    )

                sh // ""
                sh // "Subsurface mix: blend SSS with diffuse"
                sh.subsurface_mix = sh.BSDF()
                sh.subsurface_mix.response = sh.subsurface.lerp(
                    sh.diffuse_bsdf.response, sh.sss_bsdf.response
                )
                sh.subsurface_mix.throughput = sh.subsurface.lerp(
                    sh.diffuse_bsdf.throughput, sh.sss_bsdf.throughput
                )

                sh // ""
                sh // "Sheen BSDF"
                sh.sheen_bsdf_out = sh.BSDF()
                sh.sheen_bsdf_out.response = [0.0, 0.0, 0.0]
                sh.sheen_bsdf_out.throughput = [1.0, 1.0, 1.0]
                sh.mx_sheen_bsdf(
                    closureData=sh.closureData,
                    weight=sh.sheen,
                    color=sh.sheen_color,
                    roughness=sh.sheen_roughness,
                    normal=sh.normal,
                    mode=0,
                    bsdf=sh.sheen_bsdf_out,
                )

                sh // ""
                sh // "Sheen layer: sheen over subsurface mix"
                sh.bsdf.response = (
                    sh.sheen_bsdf_out.response
                    + sh.subsurface_mix.response * sh.sheen_bsdf_out.throughput
                )
                sh.bsdf.throughput = (
                    sh.sheen_bsdf_out.throughput * sh.subsurface_mix.throughput
                )

                sh // ""
                sh // "Transmission roughness (coat-affected)"
                sh.transmission_roughness_clamped = (
                    (sh.specular_roughness + sh.transmission_extra_roughness)
                    .clamp(0.0, 1.0)
                )
                sh.transmission_roughness_scalar = (
                    sh.transmission_roughness_clamped
                    * (sh.Float(1) - sh.coat_roughness_factor)
                    + sh.coat_roughness_factor
                )
                sh.transmission_roughness = sh.Float2()
                sh.mx_roughness_anisotropy(
                    roughness=sh.transmission_roughness_scalar,
                    anisotropy=sh.specular_anisotropy,
                    out_=sh.transmission_roughness,
                )

                sh // ""
                sh // "Transmission BSDF (dielectric transmission)"
                sh.transmission_bsdf = sh.BSDF()
                sh.transmission_bsdf.response = [0.0, 0.0, 0.0]
                sh.transmission_bsdf.throughput = [1.0, 1.0, 1.0]
                sh.mx_dielectric_bsdf(
                    closureData=sh.closureData,
                    weight=1.0,
                    tint=sh.transmission_color,
                    ior=sh.specular_IOR,
                    roughness=sh.transmission_roughness,
                    retroreflective=False,
                    thinfilm_thickness=0.0,
                    thinfilm_ior=1.5,
                    normal=sh.normal,
                    tangent=sh.main_tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    scatter_mode=self._SCATTER_T,
                    bsdf=sh.transmission_bsdf,
                )

                sh // ""
                sh // "Transmission mix: blend transmission with sheen layer"
                sh.bsdf.response = sh.transmission.lerp(
                    sh.bsdf.response, sh.transmission_bsdf.response
                )
                sh.bsdf.throughput = sh.transmission.lerp(
                    sh.bsdf.throughput, sh.transmission_bsdf.throughput
                )

                sh // ""
                sh // "Specular BSDF (dielectric reflection)"
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
                    tangent=sh.main_tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    scatter_mode=self._SCATTER_R,
                    bsdf=sh.specular_bsdf,
                )

                sh // ""
                sh // "Layer: specular over transmission mix"
                sh.bsdf.response = (
                    sh.specular_bsdf.response
                    + sh.bsdf.response * sh.specular_bsdf.throughput
                )
                sh.bsdf.throughput = (
                    sh.specular_bsdf.throughput * sh.bsdf.throughput
                )

                sh // ""
                sh // "Artistic IOR (reflectivity/edge-color -> physical IOR/extinction)"
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

                sh // ""
                sh // "Conductor BSDF (metal reflection)"
                sh.metal_bsdf = sh.BSDF()
                sh.metal_bsdf.response = [0.0, 0.0, 0.0]
                sh.metal_bsdf.throughput = [1.0, 1.0, 1.0]
                sh.mx_conductor_bsdf(
                    closureData=sh.closureData,
                    weight=sh.metalness,
                    ior=sh.ior_n,
                    extinction=sh.ior_k,
                    roughness=sh.main_roughness,
                    retroreflective=False,
                    thinfilm_thickness=sh.thin_film_thickness,
                    thinfilm_ior=sh.thin_film_IOR,
                    normal=sh.normal,
                    tangent=sh.main_tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    bsdf=sh.metal_bsdf,
                )

                sh // ""
                sh // "Metalness mix: conductor (fg) vs specular layer (bg)"
                sh // "Conductor response is already scaled by metalness (the weight),"
                sh // "so we just add it to the attenuated specular layer."
                sh.one_minus_metalness = sh.Float(1) - sh.metalness
                sh.bsdf.response = (
                    sh.metal_bsdf.response
                    + sh.bsdf.response * sh.one_minus_metalness
                )
                sh.bsdf.throughput = (
                    sh.metal_bsdf.throughput
                    + sh.bsdf.throughput * sh.one_minus_metalness
                )

                sh // ""
                sh // "Coat attenuation: tint underlying layers by coat color"
                sh // "Float3 coercion needed: RgbF lerp result -> Float3 for BSDF multiply"
                sh.coat_attenuation = sh.Float3(
                    sh.coat.lerp(sh.RgbF(1.0), sh.coat_color)
                )
                sh.bsdf.response = sh.bsdf.response * sh.coat_attenuation
                sh.bsdf.throughput = sh.bsdf.throughput * sh.coat_attenuation

                sh // ""
                sh // "Coat roughness"
                sh.coat_roughness_vec = sh.Float2()
                sh.mx_roughness_anisotropy(
                    roughness=sh.coat_roughness,
                    anisotropy=sh.coat_anisotropy,
                    out_=sh.coat_roughness_vec,
                )

                sh // ""
                sh // "Coat BSDF (dielectric reflection)"
                sh.coat_bsdf = sh.BSDF()
                sh.coat_bsdf.response = [0.0, 0.0, 0.0]
                sh.coat_bsdf.throughput = [1.0, 1.0, 1.0]
                sh.mx_dielectric_bsdf(
                    closureData=sh.closureData,
                    weight=sh.coat,
                    tint=[1.0, 1.0, 1.0],
                    ior=sh.coat_IOR,
                    roughness=sh.coat_roughness_vec,
                    retroreflective=False,
                    thinfilm_thickness=0.0,
                    thinfilm_ior=1.5,
                    normal=sh.coat_normal,
                    tangent=sh.coat_tangent,
                    distribution=self._DISTRIBUTION_GGX,
                    scatter_mode=self._SCATTER_R,
                    bsdf=sh.coat_bsdf,
                )

                sh // ""
                sh // "Coat layer: coat over attenuated base"
                sh.bsdf.response = (
                    sh.coat_bsdf.response
                    + sh.bsdf.response * sh.coat_bsdf.throughput
                )
                sh.bsdf.throughput = (
                    sh.coat_bsdf.throughput * sh.bsdf.throughput
                )

            test_ctx.add_node_impl(
                func_name=self._FUNC_NAME,
                mx_doc_string=(
                    "Metashade Standard Surface BSDF"
                ),
            )
