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
SUBDIR = "standard_surface"

_SURFACESHADER_NODEDEF = "ND_standard_surface_surfaceshader"


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
    Lobe("subsurface", "subsurface",
         frozenset({"subsurface", "subsurface_color", "subsurface_radius",
                    "subsurface_scale", "subsurface_anisotropy",
                    "thin_walled"}),
         ("translucent_bsdf", "subsurface_bsdf")),
    Lobe("coat", "coat",
         frozenset({"coat", "coat_color", "coat_roughness", "coat_anisotropy",
                    "coat_rotation", "coat_IOR", "coat_normal",
                    "coat_affect_color", "coat_affect_roughness"}),
         ()),
    Lobe("sheen", "sheen",
         frozenset({"sheen", "sheen_color", "sheen_roughness"}),
         ("sheen_bsdf",)),
    Lobe("transmission", "transmission",
         frozenset({"transmission", "transmission_color",
                    "transmission_extra_roughness"}),
         ()),
    Lobe("metalness", "metalness",
         frozenset({"metalness"}),
         ("conductor_bsdf", "artistic_ior")),
    Lobe("thin_film", "thin_film_thickness",
         frozenset({"thin_film_thickness", "thin_film_IOR"}),
         ()),
    Lobe("emission", "emission",
         frozenset(),
         (),
         ("emission", "emission_color")),
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
    coat: bool = True
    sheen: bool = True
    transmission: bool = True
    metalness: bool = True
    thin_film: bool = True
    emission: bool = True

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

    @staticmethod
    def from_material(
        ss_node: mx.Node,
        nodedef: mx.NodeDef,
    ) -> Permutation:
        """Determine the permutation for a ``standard_surface`` node.

        Inspects each lobe's gate input on *ss_node*:

        - Not set on the node → use the nodedef default (0 = inactive).
        - Connected (has ``nodename``, ``nodegraph``, or
          ``interfacename``) → conservatively assume active.
        - Literal value → active if non-zero.
        """
        kwargs: dict[str, bool] = {}
        for lobe in LOBES:
            inp = ss_node.getInput(lobe.gate_input)
            if inp is None:
                nd_inp = nodedef.getActiveInput(lobe.gate_input)
                active = float(nd_inp.getValueString()) != 0.0
            elif (inp.getNodeName()
                  or inp.getNodeGraphString()
                  or inp.getInterfaceName()):
                active = True
            else:
                try:
                    active = float(inp.getValueString()) != 0.0
                except (ValueError, TypeError):
                    active = True
            kwargs[lobe.name] = active
        return Permutation(**kwargs)


Permutation.ALL = Permutation()


# ---------------------------------------------------------------------------
# Codegen constants
# ---------------------------------------------------------------------------

# MaterialX GLSL enum constants (from mx_closure_type.glsl / pbrlib)
_SCATTER_R = 0
_SCATTER_T = 1
_DISTRIBUTION_GGX = 0

_STDLIB_IMPORTS = (
    "roughness_anisotropy",
    "oren_nayar_diffuse_bsdf",
    "translucent_bsdf",
    "subsurface_bsdf",
    "sheen_bsdf",
    "dielectric_bsdf",
    "conductor_bsdf",
    "artistic_ior",
)

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


def generate(
    ctx: GlslGeneratorContext,
    stdlib_doc: mx.Document,
    perm: Permutation = Permutation.ALL,
):
    """Generate the Standard Surface BSDF source-code node.

    Args:
        ctx: A production generator context (or any subclass such as
             ``GlslTestContext``).  Only the ``_sh`` generator and
             ``add_node_impl`` method are used.
        stdlib_doc: A MaterialX document with the standard library loaded.
        perm: Which lobes to emit.  ``Permutation.ALL`` (default) generates
              the full BSDF.  Disabled lobes are pruned at code-generation
              time (design-time ``if``, not runtime).
    """
    func_name = _FUNC_NAME_BASE + perm.variant_suffix + _FUNC_NAME_TYPE

    sh = ctx._sh

    register_mtlx_closure_structs(sh)
    _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, _STDLIB_IMPORTS)
    sh.instantiate(_mx_metashade_rotate_vector3)

    surfaceshader_nodedef = stdlib_doc.getNodeDef(_SURFACESHADER_NODEDEF)
    assert surfaceshader_nodedef is not None, (
        f"Could not find {_SURFACESHADER_NODEDEF}"
    )
    params = _build_bsdf_params(sh, surfaceshader_nodedef)

    with sh.function(func_name)(**params):
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
        # RgbF workaround: exponent is unitless, not a color (#224)
        sh.coat_gamma = sh.RgbF(
            sh.coat.clamp(0.0, 1.0) * sh.coat_affect_color + 1.0
        )
        sh.coat_affected_diffuse_color = (
            sh.base_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
        )

        if perm.subsurface:
            sh // ""
            sh // "Coat affect subsurface color"
            # RgbF workaround: exponent is unitless, not a color (#224)
            sh.coat_affected_subsurface_color = (
                sh.subsurface_color.clamp(0.0, 1.0).pow(sh.coat_gamma)
            )

        sh // ""
        sh // "Diffuse BSDF (Oren-Nayar)"
        sh // "`energy_compensation=false` to match the Standard Surface spec, "
        sh // "instead of the more physically-correct `true` in OpenPBR"
        sh.diffuse_bsdf = sh.BSDF(
            response = sh.Float3(0), throughput = sh.Float3(1)
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

        if perm.subsurface:
            sh // ""
            sh // "Subsurface scattering"
            sh.subsurface_radius_scaled = sh.subsurface_radius * sh.subsurface_scale
            sh.sss_bsdf = sh.BSDF(
                response = sh.Float3(0), throughput = sh.Float3(1)
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
            response = sh.Float3(0), throughput = sh.Float3(1)
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
            response = sh.Float3(0), throughput = sh.Float3(1)
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
            response = sh.Float3(0), throughput = sh.Float3(1)
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
        sh.metal_bsdf = sh.BSDF(
            response = sh.Float3(0), throughput = sh.Float3(1)
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
        sh.coat_bsdf = sh.BSDF(
            response = sh.Float3(0), throughput = sh.Float3(1)
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
        func_name=func_name,
        mx_doc_string="Metashade Standard Surface BSDF",
    )


# ---------------------------------------------------------------------------
# Surfaceshader nodegraph generation
# ---------------------------------------------------------------------------

_NODEGRAPH_NAME = "NG_metashade_standard_surface"
_BSDF_NODE_CATEGORY = FUNC_NAME.removeprefix("mx_")


def generate_surfaceshader_nodegraph(
    stock_nodedef: mx.NodeDef,
    bsdf_category: str = _BSDF_NODE_CATEGORY,
    nodegraph_name: str = _NODEGRAPH_NAME,
    target_nodedef_name: str = _SURFACESHADER_NODEDEF,
) -> mx.Document:
    """Build the surfaceshader nodegraph that wires the BSDF to a surface.

    Produces a nodegraph wiring the BSDF source-code node, emission,
    opacity, and the ``surface`` constructor.

    The *bsdf_category* / *nodegraph_name* / *target_nodedef_name*
    parameters are overridable so that variant permutations can reuse
    the same builder with different names.

    Returns a :class:`mx.Document` ready to be written with
    :func:`mx.writeToXmlFile`.
    """
    doc = mx.createDocument()

    ng = doc.addNodeGraph(nodegraph_name)
    ng.setNodeDefString(target_nodedef_name)

    # --- BSDF node ---
    bsdf_node = ng.addNode(bsdf_category, "std_surface", "BSDF")
    for inp in stock_nodedef.getActiveInputs():
        name = inp.getName()
        if name not in _BSDF_INPUTS:
            continue
        bsdf_node.addInput(name, inp.getType()).setInterfaceName(name)

    # --- Emission chain ---
    emission_weight = ng.addNode("multiply", "emission_weight", "color3")
    emission_weight.addInput("in1", "color3").setInterfaceName("emission_color")
    emission_weight.addInput("in2", "float").setInterfaceName("emission")

    emission_edf = ng.addNode("uniform_edf", "emission_edf", "EDF")
    emission_edf.addInput("color", "color3").setNodeName("emission_weight")

    # --- Opacity chain ---
    opacity_lum = ng.addNode("luminance", "opacity_luminance", "color3")
    opacity_lum.addInput("in", "color3").setInterfaceName("opacity")

    opacity_float = ng.addNode("extract", "opacity_luminance_float", "float")
    opacity_float.addInput("in", "color3").setNodeName("opacity_luminance")
    opacity_float.addInput("index", "integer").setValueString("0")

    # --- Surface constructor ---
    surface = ng.addNode("surface", "surface_ctor", "surfaceshader")
    surface.addInput("bsdf", "BSDF").setNodeName("std_surface")
    surface.addInput("edf", "EDF").setNodeName("emission_edf")
    surface.addInput("opacity", "float").setNodeName("opacity_luminance_float")

    # --- Output ---
    ng.addOutput("out", "surfaceshader").setNodeName("surface_ctor")

    return doc
