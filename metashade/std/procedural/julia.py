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
    Color of the Julia set of z^2 + c, centered on texcoord 0.5.

    Points in the set are black, and escaping points cycle through a
    cosine palette with the number of iterations before they escape.

    Args:
        texcoord: Point in the complex plane, before scaling
        cx: Real part of the constant c
        cy: Imaginary part of the constant c
        scale: Extent of the complex plane per unit of texcoord
        max_iterations: Maximum number of iterations of z^2 + c
        phase: Offset of the color palette
    """
    sh.zx = (texcoord.x - 0.5) * scale
    sh.zy = (texcoord.y - 0.5) * scale
    sh.count = sh.Float(0.0)

    # Escaped points stop updating rather than breaking out of the loop.
    with sh.for_(i=max_iterations):
        with sh.if_(sh.zx * sh.zx + sh.zy * sh.zy < 4.0):
            sh.next_zx = sh.zx * sh.zx - sh.zy * sh.zy + cx
            sh.zy = sh.zx * sh.zy * 2.0 + cy
            sh.zx = sh.next_zx
            sh.count += 1.0

    with sh.if_(sh.zx * sh.zx + sh.zy * sh.zy < 4.0):
        sh.return_(sh.RgbF(0.0))

    sh.hue = sh.count * 0.23 + phase
    sh.return_(sh.RgbF((
        sh.hue.sin() * 0.5 + 0.5,
        (sh.hue + 2.09439).sin() * 0.5 + 0.5,
        (sh.hue + 4.18879).sin() * 0.5 + 0.5,
    )))
