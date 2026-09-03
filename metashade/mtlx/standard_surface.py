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
Metashade reimplementation of the MaterialX Standard Surface BSDF.

Two-layer architecture:

1. A BSDF-outputting source-code node (``metashade_standard_surface_bsdf``) that
   receives ``ClosureData`` injection from the shader generator and
   calls stdlib BSDFs (Oren-Nayar diffuse, dielectric specular).

2. A thin hand-written nodegraph that wires the BSDF to the stock
   ``surface`` constructor, overriding ``ND_standard_surface_surfaceshader``.
   The nodegraph ships alongside this module in ``libraries/standard_surface/``
   and is loadable via the standard MaterialX ``loadLibraries`` API.
"""

from __future__ import annotations

from dataclasses import dataclass

import MaterialX as mx

from metashade.mtlx.generate import GlslGeneratorContext
from metashade.mtlx.mtlx_reflection import acquire_function
from metashade.mtlx.dtypes import (
    mtlx_to_metashade_dtype,
    register_mtlx_closure_structs,
)

_FUNC_NAME_BASE = "mx_metashade_standard_surface"
_FUNC_NAME_TYPE = "_bsdf"
FUNC_NAME = _FUNC_NAME_BASE + _FUNC_NAME_TYPE

_SURFACESHADER_NODEDEF = "ND_standard_surface_surfaceshader"
_NODEGRAPH_NAME = "NG_metashade_standard_surface"


# ---------------------------------------------------------------------------
# Lobe pruning data model (issue #233)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Lobe:
    """A prunable Standard Surface feature bundle.

    Each lobe groups the gate input that enables it, the BSDF function
    parameters it owns, the stdlib ``#include`` s it requires, and any
    nodegraph-only inputs (e.g. emission).
    """
    name: str
    gate_input: str
    params: frozenset[str]
    stdlib_imports: tuple[str, ...]
    nodegraph_inputs: tuple[str, ...] = ()


LOBES: tuple[Lobe, ...] = (
    Lobe(
        name="subsurface",
        gate_input="subsurface",
        params=frozenset({
            "subsurface", "subsurface_color", "subsurface_radius",
            "subsurface_scale", "subsurface_anisotropy",
            "thin_walled",
        }),
        stdlib_imports=("translucent_bsdf", "subsurface_bsdf"),
    ),
)

_LOBES_BY_NAME: dict[str, Lobe] = {lobe.name: lobe for lobe in LOBES}


@dataclass(frozen=True)
class Permutation:
    """Identifies a specific Standard Surface specialization.

    Each boolean field corresponds to a :class:`Lobe`.  ``True`` means the
    lobe is emitted; ``False`` means it is pruned.  All default to ``True``
    (full SS, backward compatible).

    Naming is *subtractive*: :attr:`variant_suffix` lists disabled lobes
    with a ``0`` suffix (e.g. ``_subsurface0``).  This is stable under
    progressive development — adding coat pruning later does not rename
    existing ``_subsurface0`` variants.
    """
    subsurface: bool = True

    @property
    def variant_suffix(self) -> str:
        """Subtractive suffix for file/node naming, e.g. ``_subsurface0``.

        Returns an empty string for the full permutation (all lobes on).
        """
        disabled = sorted(
            lobe.name for lobe in LOBES
            if not getattr(self, lobe.name)
        )
        if not disabled:
            return ""
        return "_" + "_".join(f"{d}0" for d in disabled)

    @property
    def func_name(self) -> str:
        """Full function name for the generated BSDF node."""
        return _FUNC_NAME_BASE + self.variant_suffix + _FUNC_NAME_TYPE

    @property
    def bsdf_category(self) -> str:
        """MaterialX node category (func_name without the ``mx_`` prefix)."""
        return self.func_name.removeprefix("mx_")

    @property
    def nodegraph_name(self) -> str:
        """Nodegraph name for the surfaceshader wiring."""
        return _NODEGRAPH_NAME + self.variant_suffix

    @property
    def surfaceshader_filename(self) -> str:
        """Output ``.mtlx`` filename for the surfaceshader nodegraph."""
        return f"{_FUNC_NAME_BASE}{self.variant_suffix}_surfaceshader.mtlx"

    def generate_bsdf(
        self,
        ctx: GlslGeneratorContext,
        stdlib_doc: mx.Document,
    ):
        """Generate the Standard Surface BSDF source-code node.

        Args:
            ctx: A production generator context (or any subclass such as
                 ``GlslTestContext``).  Only the ``_sh`` generator and
                 ``add_node_impl`` method are used.
            stdlib_doc: A MaterialX document with the standard library loaded.
        """
        sh = ctx._sh

        register_mtlx_closure_structs(sh)

        stdlib_imports = _BASE_STDLIB_IMPORTS | frozenset().union(*(
            lobe.stdlib_imports for lobe in LOBES
            if getattr(self, lobe.name)
        ))

        _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, stdlib_imports)
        sh.instantiate(_mx_metashade_rotate_vector3)

        params = _build_bsdf_params(sh)

        with sh.function(self.func_name)(**params):
            sh // ""
            sh // "Coat affect roughness: blend specular roughness toward 1.0"
            sh.coat_roughness_factor = (
                sh.coat_affect_roughness * sh.coat * sh.coat_roughness
            )
            sh.coat_affected_specular_roughness = (
                sh.specular_roughness
                * (sh.Float(1) - sh.coat_roughness_factor)
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
                sh._mx_metashade_rotate_vector3(
                    in_=sh.tangent,
                    amount=sh.tangent_rotate_degree,
                    axis=sh.normal,
                    result=sh.tangent_rotated,
                )
                sh.main_tangent = sh.tangent_rotated.normalize()

            sh // ""
            sh // "Coat tangent rotation"
            sh.coat_tangent = sh.tangent
            with sh.if_(sh.coat_anisotropy > 0.0):
                sh.coat_tangent_rotate_degree = sh.coat_rotation * 360.0
                sh.coat_tangent_rotated = sh.Float3()
                sh._mx_metashade_rotate_vector3(
                    in_=sh.tangent,
                    amount=sh.coat_tangent_rotate_degree,
                    axis=sh.coat_normal,
                    result=sh.coat_tangent_rotated,
                )
                sh.coat_tangent = sh.coat_tangent_rotated.normalize()

            sh // ""
            sh // "Coat affect color: darken diffuse under the coat"
            sh.coat_gamma = sh.RgbF(
                sh.coat.clamp(0.0, 1.0) * sh.coat_affect_color + 1.0
            )
            sh.coat_affected_diffuse_color = (
                sh.base_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
            )

            if self.subsurface:
                sh // ""
                sh // "Coat affect subsurface color"
                sh.coat_affected_subsurface_color = (
                    sh.subsurface_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
                )

            sh // ""
            sh // "Diffuse BSDF (Oren-Nayar)"
            sh // ("`energy_compensation=false` to match the Standard "
                   "Surface spec, ")
            sh // "instead of the more physically-correct `true` in OpenPBR"
            sh.diffuse_bsdf = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
            sh.mx_oren_nayar_diffuse_bsdf(
                closureData=sh.closureData,
                weight=sh.base,
                color=sh.coat_affected_diffuse_color,
                roughness=sh.diffuse_roughness,
                normal=sh.normal,
                energy_compensation=False,
                bsdf=sh.diffuse_bsdf,
            )

            if self.subsurface:
                sh // ""
                sh // "Subsurface scattering"
                sh.subsurface_radius_scaled = (
                    sh.subsurface_radius * sh.subsurface_scale
                )
                sh.sss_bsdf = sh.BSDF(
                    response=sh.Float3(0), throughput=sh.Float3(1)
                )
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
            else:
                sh.subsurface_mix = sh.diffuse_bsdf

            sh // ""
            sh // "Sheen BSDF"
            sh.sheen_bsdf_out = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
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
            sh.transmission_bsdf = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
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
                distribution=_DISTRIBUTION_GGX,
                scatter_mode=_SCATTER_T,
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
            sh.specular_bsdf = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
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
                distribution=_DISTRIBUTION_GGX,
                scatter_mode=_SCATTER_R,
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
            sh // ("Artistic IOR (reflectivity/edge-color -> physical "
                   "IOR/extinction)")
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
            sh.metal_bsdf = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
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
                distribution=_DISTRIBUTION_GGX,
                bsdf=sh.metal_bsdf,
            )

            sh // ""
            sh // "Metalness mix: conductor (fg) vs specular layer (bg)"
            sh // ("Conductor response is already scaled by metalness "
                   "(the weight),")
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
            sh // ("Float3 coercion needed: RgbF lerp result -> "
                   "Float3 for BSDF multiply")
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
            sh.coat_bsdf = sh.BSDF(
                response=sh.Float3(0), throughput=sh.Float3(1)
            )
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
                distribution=_DISTRIBUTION_GGX,
                scatter_mode=_SCATTER_R,
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

        ctx.add_node_impl(
            func_name=self.func_name,
            mx_doc_string="Metashade Standard Surface BSDF",
        )

    def generate_surfaceshader_nodegraph(self) -> mx.Document:
        """Build the surfaceshader nodegraph that wires the BSDF to a surface.

        Produces a nodegraph wiring the BSDF source-code node, emission,
        opacity, and the ``surface`` constructor.

        Returns a :class:`mx.Document` ready to be written with
        :func:`mx.writeToXmlFile`.
        """
        doc = mx.createDocument()

        ng = doc.addNodeGraph(self.nodegraph_name)
        ng.setNodeDefString(_SURFACESHADER_NODEDEF)

        bsdf_node = ng.addNode(self.bsdf_category, "std_surface", "BSDF")
        for name, mtlx_type in _BSDF_INPUTS.items():
            bsdf_node.addInput(name, mtlx_type).setInterfaceName(name)

        emission_weight = ng.addNode("multiply", "emission_weight", "color3")
        emission_weight.addInput("in1", "color3").setInterfaceName(
            "emission_color"
        )
        emission_weight.addInput("in2", "float").setInterfaceName("emission")

        emission_edf = ng.addNode("uniform_edf", "emission_edf", "EDF")
        emission_edf.addInput("color", "color3").setNodeName("emission_weight")

        opacity_lum = ng.addNode("luminance", "opacity_luminance", "color3")
        opacity_lum.addInput("in", "color3").setInterfaceName("opacity")

        opacity_float = ng.addNode(
            "extract", "opacity_luminance_float", "float"
        )
        opacity_float.addInput("in", "color3").setNodeName(
            "opacity_luminance"
        )
        opacity_float.addInput("index", "integer").setValueString("0")

        surface = ng.addNode("surface", "surface_ctor", "surfaceshader")
        surface.addInput("bsdf", "BSDF").setNodeName("std_surface")
        surface.addInput("edf", "EDF").setNodeName("emission_edf")
        surface.addInput("opacity", "float").setNodeName(
            "opacity_luminance_float"
        )

        ng.addOutput("out", "surfaceshader").setNodeName("surface_ctor")

        return doc

Permutation.ALL = Permutation()


# ---------------------------------------------------------------------------
# Codegen constants
# ---------------------------------------------------------------------------

# MaterialX GLSL enum constants (from mx_closure_type.glsl / pbrlib)
_SCATTER_R = 0
_SCATTER_T = 1
_DISTRIBUTION_GGX = 0

_BASE_STDLIB_IMPORTS = frozenset({
    "roughness_anisotropy",
    "oren_nayar_diffuse_bsdf",
    "sheen_bsdf",
    "dielectric_bsdf",
    "conductor_bsdf",
    "artistic_ior",
})

_BSDF_INPUTS: dict[str, str] = {
    "base": "float", "base_color": "color3", "diffuse_roughness": "float",
    "metalness": "float",
    "specular": "float", "specular_color": "color3",
    "specular_roughness": "float",
    "specular_IOR": "float", "specular_anisotropy": "float",
    "specular_rotation": "float",
    "sheen": "float", "sheen_color": "color3", "sheen_roughness": "float",
    "coat": "float", "coat_color": "color3", "coat_roughness": "float",
    "coat_anisotropy": "float",
    "coat_rotation": "float", "coat_IOR": "float", "coat_normal": "vector3",
    "coat_affect_color": "float", "coat_affect_roughness": "float",
    "subsurface": "float", "subsurface_color": "color3",
    "subsurface_radius": "color3",
    "subsurface_scale": "float", "subsurface_anisotropy": "float",
    "thin_walled": "boolean",
    "transmission": "float", "transmission_color": "color3",
    "transmission_extra_roughness": "float",
    "thin_film_thickness": "float", "thin_film_IOR": "float",
    "normal": "vector3", "tangent": "vector3",
}


def _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, node_names):
    """Resolve, include, and acquire stdlib sourcecode nodes.

    Nodes are grouped by header file.  Both the ``#include`` directives
    and the function acquisitions within each header are emitted in
    sorted order for deterministic output.
    """
    all_impls = stdlib_doc.getImplementations()
    by_file: dict[str, list[tuple[str, object]]] = {}
    for name in node_names:
        impl = next(
            (i for i in all_impls
             if i.getNodeDefString().endswith(name)
             and i.getTarget() == "genglsl"),
            None,
        )
        assert impl is not None, (
            f"Could not find genglsl impl for {name}"
        )
        file_path = impl.getAttribute("file")
        by_file.setdefault(file_path, []).append((name, impl))

    for file_path in sorted(by_file):
        sh.include(file_path)
        for _, impl in sorted(by_file[file_path]):
            acquire_function(sh, impl)


def _build_bsdf_params(sh):
    """Build BSDF node params from the hardcoded input type map.

    Types come from :data:`_BSDF_INPUTS` so that ``color3`` vs
    ``vector3`` distinctions match the stock surfaceshader nodedef.
    ``closureData`` is placed first and the BSDF output is last.
    """
    params = {"closureData": sh.ClosureData}

    for name, mtlx_type in _BSDF_INPUTS.items():
        dtype = mtlx_to_metashade_dtype(mtlx_type, sh)
        assert dtype is not None, (
            f"Unmappable type for {name}: {mtlx_type}"
        )
        params[name] = dtype

    params["bsdf"] = sh.InOut(sh.BSDF)
    return params


def _mx_metashade_rotate_vector3(
    sh, in_: Float3, amount: Float, axis: Float3,
    result: Out[Float3],
):
    """Rodrigues' rotation formula.

    Private copy of the stdlib rotate3d helper.  Avoids
    duplicate-definition errors when the material's own nodegraph
    also uses rotate3d nodes, which would cause the generator to
    emit mx_rotate_vector3 a second time
    (see https://github.com/metashade/metashade/issues/230).
    """
    sh.axis_n = axis.normalize()
    sh.rad = amount.radians()
    sh.s = sh.rad.sin()
    sh.c = sh.rad.cos()
    result._ = (
        in_ * sh.c
        + in_.cross(sh.axis_n) * sh.s
        + sh.axis_n * sh.axis_n.dot(in_) * (sh.Float(1) - sh.c)
    )
