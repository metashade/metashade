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
Metashade wrapper for MaterialX generalized_schlick_bsdf node.

This module provides a stub implementation that can be used to validate
the override infrastructure. The actual PBR calculations will be added later.
"""

from metashade.modules import export


@export
def mx_metashade_generalized_schlick_bsdf(
    sh,
    weight: 'Float',
    color0: 'RgbF',
    color90: 'RgbF',
    exponent: 'Float',
    result: 'Out[RgbF]'
):
    """
    Metashade wrapper for generalized_schlick_bsdf (stub).
    
    This is a simplified stub to validate the override infrastructure.
    The full implementation will match MaterialX's signature:
    - ClosureData closureData
    - float weight
    - vec3 color0, color82, color90
    - float exponent
    - vec2 roughness
    - float thinfilm_thickness, thinfilm_ior
    - vec3 N, X
    - int distribution, scatter_mode
    - inout BSDF bsdf
    
    For now, just returns color0 scaled by weight.
    """
    sh.result = sh.color0 * sh.weight
