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
Julia set fractals.

References:
    https://en.wikipedia.org/wiki/Julia_set
"""

from metashade.modules import export


@export
def julia2d(
    sh,
    texcoord: 'Float2',
    cx: 'Float' = -0.74543,
    cy: 'Float' = 0.11301,
    scale: 'Float' = 3.0,
    max_iterations: 'Int' = 64,
    phase: 'Float' = 0.0,
) -> 'RgbF':
    """
    Color of the Julia set of z^2 + c, a placeholder returning hot pink.

    Args:
        texcoord: Point in the complex plane, before scaling
        cx: Real part of the constant c
        cy: Imaginary part of the constant c
        scale: Extent of the complex plane per unit of texcoord
        max_iterations: Maximum number of iterations of z^2 + c
        phase: Offset of the color palette
    """
    sh.return_(sh.RgbF((1.0, 0.0, 0.5)))
