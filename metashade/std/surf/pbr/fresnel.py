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
Fresnel term approximations for specular reflection.

References:
    https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/fresnel(specularf)
"""

from metashade.modules import export


@export
def F_Schlick(sh, LdotH: 'Float', rgbF0: 'RgbF') -> 'RgbF':
    """
    Schlick's approximation of the Fresnel term.
    
    Args:
        LdotH: Dot product of light direction and half-vector
        rgbF0: Reflectance at normal incidence
    
    Returns:
        Fresnel reflectance
    """
    sh.return_(
        rgbF0 + (sh.RgbF(1.0) - rgbF0)
            * (sh.Float(1.0) - LdotH).pow(sh.Float(5.0))
    )
