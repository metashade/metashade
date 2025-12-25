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
Diffuse BRDF terms.

References:
    https://google.github.io/filament/Filament.md.html#materialsystem/diffusebrdf
"""

import math
from metashade.modules import export


@export
def Fd_Lambert(sh) -> 'Float':
    """
    Lambertian diffuse BRDF.
    
    Returns the constant 1/π factor for energy-conserving Lambertian diffuse.
    Multiply by the diffuse albedo to get the full diffuse contribution.
    
    Returns:
        1/π (the Lambertian BRDF normalization factor)
    
    Reference:
        https://google.github.io/filament/Filament.md.html#materialsystem/diffusebrdf
    """
    sh.return_(sh.Float(1.0 / math.pi))
