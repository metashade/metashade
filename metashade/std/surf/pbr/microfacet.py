# Copyright 2025 Pavlo Penenko
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
Microfacet model functions: Normal Distribution Functions (NDF) and
Geometric Shadowing/Visibility terms.

References:
    https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf
"""

import math
from metashade.modules import export


@export
def D_Ggx(sh, NdotH: 'Float', fAlphaRoughness: 'Float') -> 'Float':
    """
    GGX/Trowbridge-Reitz Normal Distribution Function.
    
    Args:
        NdotH: Dot product of surface normal and half-vector
        fAlphaRoughness: Roughness parameter (perceptualRoughness^2)
    
    Returns:
        NDF value
    """
    sh // "https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/normaldistributionfunction(speculard)"
    sh // ""
    sh.fASqr = fAlphaRoughness * fAlphaRoughness
    sh.fF = (NdotH * sh.fASqr - NdotH) * NdotH + sh.Float(1.0)
    sh.return_(
        (sh.fASqr / (sh.Float(math.pi) * sh.fF * sh.fF)).saturate()
    )


@export
def V_SmithGgxCorrelated(
    sh,
    NdotV: 'Float',
    NdotL: 'Float',
    fAlphaRoughness: 'Float'
) -> 'Float':
    """
    Smith-GGX Height-Correlated Visibility Function.
    
    This is the visibility term, combining
    the geometric shadowing and masking into a single optimized form.
    
    Args:
        NdotV: Dot product of surface normal and view direction
        NdotL: Dot product of surface normal and light direction
        fAlphaRoughness: Roughness parameter (perceptualRoughness^2)
    
    Returns:
        Visibility term value
    """
    sh // "https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/geometricshadowing(specularg)"
    sh // ""
    sh.fASqr = fAlphaRoughness * fAlphaRoughness
    sh.fGgxL = NdotV * (
        (NdotL - NdotL * sh.fASqr) * NdotL + sh.fASqr
    ).sqrt()
    sh.fGgxV = NdotL * (
        (NdotV - NdotV * sh.fASqr) * NdotV + sh.fASqr
    ).sqrt()
    sh.fV = sh.Float(0.5) / (sh.fGgxL + sh.fGgxV)
    sh.return_(sh.fV.saturate())
