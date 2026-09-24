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

_STDLIB_SURFACESHADER_NODEDEF = "ND_standard_surface_surfaceshader"
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


@dataclass(frozen=True)
class InputMetadata:
    mtlx_type: str
    doc: str
    default_value: str = ""
    defaultgeomprop: str = ""


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
    Lobe(
        name="sheen",
        gate_input="sheen",
        params=frozenset({
            "sheen", "sheen_color", "sheen_roughness",
        }),
        stdlib_imports=("sheen_bsdf",),
    ),
    Lobe(
        name="transmission",
        gate_input="transmission",
        params=frozenset({
            "transmission", "transmission_color",
            "transmission_extra_roughness",
        }),
        # dielectric_bsdf shared with specular and coat.
        stdlib_imports=("dielectric_bsdf",),
    ),
    Lobe(
        name="metalness",
        gate_input="metalness",
        params=frozenset({
            "metalness",
        }),
        stdlib_imports=("conductor_bsdf", "artistic_ior"),
    ),
    Lobe(
        name="coat",
        gate_input="coat",
        params=frozenset({
            "coat", "coat_color", "coat_roughness", "coat_anisotropy",
            "coat_rotation", "coat_IOR", "coat_normal",
            "coat_affect_color", "coat_affect_roughness",
        }),
        # dielectric_bsdf shared with specular and transmission;
        # currently in _BASE_STDLIB_IMPORTS but listed here so the
        # import is preserved when the base set is refined.
        stdlib_imports=("dielectric_bsdf",),
    ),
)

_LOBES_BY_NAME: dict[str, Lobe] = {lobe.name: lobe for lobe in LOBES}


class LobeFlags:
    """Boolean flags for each prunable lobe, with attribute access.

    Built from :data:`LOBES`; each lobe name becomes a bool attribute.
    Defaults to all lobes active.
    """
    __slots__ = tuple(lobe.name for lobe in LOBES)

    def __init__(self, **kwargs: bool):
        unknown = kwargs.keys() - {lobe.name for lobe in LOBES}
        if unknown:
            raise TypeError(
                f"Unknown lobe(s): {', '.join(sorted(unknown))}"
            )
        for lobe in LOBES:
            object.__setattr__(
                self, lobe.name, kwargs.get(lobe.name, True),
            )

    def __setattr__(self, name, value):
        raise AttributeError("LobeFlags is immutable")

    def __delattr__(self, name):
        raise AttributeError("LobeFlags is immutable")

    @property
    def name_suffix(self) -> str:
        """Subtractive suffix, e.g. ``_coat0_subsurface0``."""
        disabled = sorted(
            lobe.name for lobe in LOBES
            if not getattr(self, lobe.name)
        )
        if not disabled:
            return ""
        return "_" + "_".join(f"{d}0" for d in disabled)

    @property
    def pruned_params(self) -> frozenset[str]:
        """Union of params from all disabled lobes."""
        return frozenset().union(*(
            lobe.params for lobe in LOBES
            if not getattr(self, lobe.name)
        ))

    @property
    def stdlib_imports(self) -> frozenset[str]:
        """Union of stdlib imports from all active lobes."""
        return frozenset().union(*(
            lobe.stdlib_imports for lobe in LOBES
            if getattr(self, lobe.name)
        ))


# ---------------------------------------------------------------------------
# Generated helper functions (emitted via sh.instantiate)
# ---------------------------------------------------------------------------

def _mx_metashade_rotate_vector3(
    sh, in_: Float3, amount: Float, axis: Float3,
) -> Float3:
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
    sh.return_(
        in_ * sh.c
        + in_.cross(sh.axis_n) * sh.s
        + sh.axis_n * sh.axis_n.dot(in_) * (sh.Float(1) - sh.c)
    )


def _mx_metashade_rotate_tangent(
    sh, tangent: Float3, anisotropy: Float, rotation: Float,
    axis: Float3,
) -> Float3:
    """Conditionally rotate a tangent vector when anisotropy is active."""
    with sh.if_(anisotropy > 0.0):
        sh.rotate_degree = rotation * 360.0
        sh.return_(sh._mx_metashade_rotate_vector3(
            in_=tangent,
            amount=sh.rotate_degree,
            axis=axis,
        ).normalize())
    sh.return_(tangent)


class Permutation:
    """Identifies a specific Standard Surface specialization.

    *lobes* is a :class:`LobeFlags` indicating which lobes are active.
    Defaults to all lobes on (full SS, backward compatible).

    Naming is *subtractive*: :attr:`name_suffix` lists disabled lobes
    with a ``0`` suffix (e.g. ``_subsurface0``).  This is stable under
    progressive development — adding coat pruning later does not rename
    existing ``_subsurface0`` variants.
    """

    def __init__(self, stdlib_doc: mx.Document, *,
                 lobes: LobeFlags | None = None):
        self.lobes = lobes or LobeFlags()

        stdlib_surfaceshader = stdlib_doc.getNodeDef(_STDLIB_SURFACESHADER_NODEDEF)
        if stdlib_surfaceshader is None:
            raise RuntimeError(
                f"Could not find {_STDLIB_SURFACESHADER_NODEDEF} in stdlib_doc"
            )

        pruned_inputs = self.lobes.pruned_params

        self._inputs: dict[str, InputMetadata] = {}
        for inp in stdlib_surfaceshader.getActiveInputs():
            input_name = inp.getName()
            if input_name not in pruned_inputs:
                self._inputs[input_name] = InputMetadata(
                    mtlx_type=inp.getType(),
                    doc=inp.getDocString(),
                    default_value=inp.getValueString(),
                    defaultgeomprop=inp.getAttribute("defaultgeomprop"),
                )

        self._surfaceshader_category = \
            _FUNC_NAME_BASE.removeprefix("mx_") + self.name_suffix
        
        self._surfaceshader_nodedef_name = (
            f"ND_{self._surfaceshader_category}_surfaceshader"
            if self.name_suffix else _STDLIB_SURFACESHADER_NODEDEF
        )

    @property
    def name_suffix(self) -> str:
        """Subtractive suffix for file/node naming, e.g. ``_subsurface0``."""
        return self.lobes.name_suffix

    @property
    def func_name(self) -> str:
        """Full function name for the generated BSDF node."""
        return _FUNC_NAME_BASE + self.name_suffix + _FUNC_NAME_TYPE

    @property
    def bsdf_category(self) -> str:
        """MaterialX node category (func_name without the ``mx_`` prefix)."""
        return self.func_name.removeprefix("mx_")

    @property
    def nodegraph_name(self) -> str:
        """Nodegraph name for the surfaceshader wiring."""
        return _NODEGRAPH_NAME + self.name_suffix

    @property
    def surfaceshader_filename(self) -> str:
        """Output ``.mtlx`` filename for the surfaceshader nodegraph."""
        return f"{_FUNC_NAME_BASE}{self.name_suffix}_surfaceshader.mtlx"

    def _create_bsdf_function(self, sh):
        params = {"closureData": sh.ClosureData}

        for name, metadata in self._inputs.items():
            if name not in _BSDF_INPUTS:
                continue

            dtype = mtlx_to_metashade_dtype(metadata.mtlx_type, sh)
            assert dtype is not None, (
                f"Unmappable type for {name}: {metadata.mtlx_type}"
            )
            params[name] = dtype

        params["bsdf"] = sh.InOut(sh.BSDF)
        return sh.function(self.func_name)(**params)

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
            if getattr(self.lobes, lobe.name)
        ))

        _acquire_stdlib_sourcecode_nodes(sh, stdlib_doc, stdlib_imports)
        sh.instantiate(_mx_metashade_rotate_vector3)
        sh.instantiate(_mx_metashade_rotate_tangent)

        with self._create_bsdf_function(sh):
            if self.lobes.coat:
                sh // ""
                sh // "Coat affect roughness: blend specular roughness toward 1.0"
                sh.coat_roughness_factor = (
                    sh.coat_affect_roughness * sh.coat * sh.coat_roughness
                )
                sh.coat_affected_specular_roughness = \
                    sh.coat_roughness_factor.lerp(
                        sh.specular_roughness, sh.Float(1)
                    )

            sh // ""
            sh // "Roughness"
            sh.main_roughness = sh.Float2()
            sh.mx_roughness_anisotropy(
                roughness=(sh.coat_affected_specular_roughness
                           if self.lobes.coat else sh.specular_roughness),
                anisotropy=sh.specular_anisotropy,
                out_=sh.main_roughness,
            )

            sh // ""
            sh // "Tangent rotation"
            sh.main_tangent = sh._mx_metashade_rotate_tangent(
                tangent=sh.tangent,
                anisotropy=sh.specular_anisotropy,
                rotation=sh.specular_rotation,
                axis=sh.normal,
            )

            if self.lobes.coat:
                sh // ""
                sh // "Coat tangent rotation"
                sh.coat_tangent = sh._mx_metashade_rotate_tangent(
                    tangent=sh.tangent,
                    anisotropy=sh.coat_anisotropy,
                    rotation=sh.coat_rotation,
                    axis=sh.coat_normal,
                )

                sh // ""
                sh // "Coat affect color: darken diffuse under the coat"
                sh.coat_gamma = sh.RgbF(
                    sh.coat.saturate() * sh.coat_affect_color + 1.0
                )
                sh.coat_affected_diffuse_color = (
                    sh.base_color.saturate().pow(sh.coat_gamma)
                )

                if self.lobes.subsurface:
                    sh // ""
                    sh // "Coat affect subsurface color"
                    sh.subsurface_color = (
                        sh.subsurface_color.saturate().pow(sh.coat_gamma)
                    )

            sh // ""
            sh // "Diffuse BSDF (Oren-Nayar)"
            with sh.block():
                sh.diffuse_bsdf = sh.BSDF(
                    response=sh.Float3(0), throughput=sh.Float3(1)
                )

                sh // ("`energy_compensation=false` to match the Standard "
                       "Surface spec, ")
                sh // ("instead of the more physically-correct `true` "
                       "in OpenPBR")
                sh.mx_oren_nayar_diffuse_bsdf(
                    closureData=sh.closureData,
                    weight=sh.base,
                    color=(sh.coat_affected_diffuse_color
                           if self.lobes.coat else sh.base_color),
                    roughness=sh.diffuse_roughness,
                    normal=sh.normal,
                    energy_compensation=False,
                    bsdf=sh.diffuse_bsdf,
                )
                sh.bsdf = sh.diffuse_bsdf

            if self.lobes.subsurface:
                sh // ""
                sh // "Subsurface scattering"
                with sh.block():
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
                            color=sh.subsurface_color,
                            normal=sh.normal,
                            bsdf=sh.sss_bsdf,
                        )
                    with sh.else_():
                        sh.mx_subsurface_bsdf(
                            closureData=sh.closureData,
                            weight=1.0,
                            color=sh.subsurface_color,
                            radius=sh.subsurface_radius_scaled,
                            anisotropy=sh.subsurface_anisotropy,
                            normal=sh.normal,
                            bsdf=sh.sss_bsdf,
                        )

                    sh.mx_mix_bsdf(
                        closureData=sh.closureData,
                        fg=sh.sss_bsdf,
                        bg=sh.bsdf,
                        mix=sh.subsurface,
                        bsdf=sh.bsdf,
                    )

            if self.lobes.sheen:
                sh // ""
                sh // "Sheen BSDF"
                with sh.block():
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

                    sh.mx_layer_bsdf(
                        closureData=sh.closureData,
                        top=sh.sheen_bsdf_out,
                        base=sh.bsdf,
                        bsdf=sh.bsdf,
                    )

            if self.lobes.transmission:
                sh // ""
                sh // "Transmission"
                with sh.block():
                    sh.transmission_roughness_scalar = (
                        (sh.specular_roughness
                         + sh.transmission_extra_roughness)
                        .saturate()
                    )

                    if self.lobes.coat:
                        sh // "Coat-affected"
                        sh.transmission_roughness_scalar = \
                            sh.coat_roughness_factor.lerp(
                                sh.transmission_roughness_scalar,
                                sh.Float(1),
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

                    sh.mx_mix_bsdf(
                        closureData=sh.closureData,
                        fg=sh.transmission_bsdf,
                        bg=sh.bsdf,
                        mix=sh.transmission,
                        bsdf=sh.bsdf,
                    )

            sh // ""
            sh // "Specular BSDF (dielectric reflection)"
            with sh.block():
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

                sh.mx_layer_bsdf(
                    closureData=sh.closureData,
                    top=sh.specular_bsdf,
                    base=sh.bsdf,
                    bsdf=sh.bsdf,
                )

            if self.lobes.metalness:
                sh // ""
                sh // "Metalness"
                with sh.block():
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

            if self.lobes.coat:
                sh // ""
                sh // "Coat attenuation and layer"
                with sh.block():
                    sh.coat_attenuation = sh.Float3(
                        sh.coat.lerp(sh.RgbF(1.0), sh.coat_color)
                    )
                    sh.bsdf.response *= sh.coat_attenuation
                    sh.bsdf.throughput *= sh.coat_attenuation

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
                        tint=sh.RgbF(1.0),
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

                    sh.mx_layer_bsdf(
                        closureData=sh.closureData,
                        top=sh.coat_bsdf,
                        base=sh.bsdf,
                        bsdf=sh.bsdf,
                    )

        ctx.add_node_impl(
            func_name=self.func_name,
            mx_doc_string="Metashade Standard Surface BSDF",
            input_metadata=self._inputs,
        )

    def generate_surfaceshader_nodegraph(self) -> mx.Document:
        """Build the surfaceshader nodegraph (and nodedef for pruned variants).

        For the full permutation, the nodegraph overrides the stock
        ``ND_standard_surface_surfaceshader`` directly — no new nodedef
        is needed.

        Pruned permutations get their own ``surfaceshader`` nodedef
        (mirroring the stock inputs minus pruned parameters) so that
        multiple permutations can coexist in the same environment.

        Returns a :class:`mx.Document` ready to be written with
        :func:`mx.writeToXmlFile`.
        """
        doc = mx.createDocument()

        if bool(self.name_suffix):
            nodedef = doc.addNodeDef(
                self._surfaceshader_nodedef_name,
                "surfaceshader",
                self._surfaceshader_category,
            )
            for name, meta in self._inputs.items():
                nodedef_input = nodedef.addInput(name, meta.mtlx_type)
                if meta.default_value:
                    nodedef_input.setValueString(meta.default_value)
                if meta.defaultgeomprop:
                    nodedef_input.setAttribute(
                        "defaultgeomprop", meta.defaultgeomprop,
                    )
                if meta.doc:
                    nodedef_input.setDocString(meta.doc)

        nodegraph = doc.addNodeGraph(self.nodegraph_name)

        # Point nodegraph (nodeimpl) to the nodedef
        nodegraph.setNodeDefString(self._surfaceshader_nodedef_name)

        bsdf_node = nodegraph.addNode(self.bsdf_category, "std_surface", "BSDF")
        for name, metadata in self._inputs.items():
            if name in _BSDF_INPUTS:
                bsdf_node.addInput(name, metadata.mtlx_type).setInterfaceName(name)

        emission_weight = nodegraph.addNode("multiply", "emission_weight", "color3")
        emission_weight.addInput("in1", "color3").setInterfaceName(
            "emission_color"
        )
        emission_weight.addInput("in2", "float").setInterfaceName("emission")

        emission_edf = nodegraph.addNode("uniform_edf", "emission_edf", "EDF")
        emission_edf.addInput("color", "color3").setNodeName("emission_weight")

        opacity_lum = nodegraph.addNode("luminance", "opacity_luminance", "color3")
        opacity_lum.addInput("in", "color3").setInterfaceName("opacity")

        opacity_float = nodegraph.addNode(
            "extract", "opacity_luminance_float", "float"
        )
        opacity_float.addInput("in", "color3").setNodeName(
            "opacity_luminance"
        )
        opacity_float.addInput("index", "integer").setValueString("0")

        surface = nodegraph.addNode("surface", "surface_ctor", "surfaceshader")
        surface.addInput("bsdf", "BSDF").setNodeName("std_surface")
        surface.addInput("edf", "EDF").setNodeName("emission_edf")
        surface.addInput("opacity", "float").setNodeName(
            "opacity_luminance_float"
        )

        nodegraph.addOutput("out", "surfaceshader").setNodeName("surface_ctor")

        return doc



def prune_material(stdlib_doc: mx.Document, material_doc: mx.Document) -> bool:
    """Optimize a material by pruning inactive lobes per node.

    Each top-level ``standard_surface`` node is independently analyzed:
    its lobe gate inputs determine which lobes are active, a matching
    :class:`Permutation` is instantiated, and the node is rewritten to
    the pruned category with unused inputs removed.

    Modifies *material_doc* in place.  Returns whether any node was
    pruned.

    .. note::
       Only document-level nodes are analyzed and rewritten.  Nodes
       nested inside ``NodeGraph`` elements (e.g. Prism/Protein
       wrappers) are not yet handled.
    """
    any_pruned = False

    for node in material_doc.getNodes():
        if node.getCategory() != "standard_surface":
            continue

        lobe_kwargs = {}
        for lobe in LOBES:
            inp = node.getInput(lobe.gate_input)
            if inp is None:
                lobe_kwargs[lobe.name] = False
            elif inp.getNodeName() or inp.getNodeGraphString():
                lobe_kwargs[lobe.name] = True
            else:
                val = inp.getValueString()
                try:
                    lobe_kwargs[lobe.name] = float(val) != 0.0
                except (ValueError, TypeError):
                    lobe_kwargs[lobe.name] = bool(val)

        perm = Permutation(stdlib_doc, lobes=LobeFlags(**lobe_kwargs))
        if not perm.name_suffix:
            continue

        node.setCategory(perm._surfaceshader_category)
        for inp in node.getActiveInputs():
            if inp.getName() not in perm._inputs:
                node.removeInput(inp.getName())
        any_pruned = True

    return any_pruned


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
    "dielectric_bsdf",
    "layer_bsdf",
    "mix_bsdf",
})

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



