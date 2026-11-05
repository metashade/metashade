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

from metashade.modules import export

@export
def meta_squares(
    sh,
    texcoord: 'Float2',
    scale: 'Float' = 10.0,
) -> 'RgbF':
    """
    Procedural randomized cell colors with
    sinusoidal UV distortion.
    """

    # Scale UV coordinates
    sh.uv = texcoord * scale

    # Distort UVs using swapped components
    sh.warp = sh.Float2((
        (sh.uv.y * scale).sin(),
        (sh.uv.x * scale).sin()
    ))

    sh.uv += sh.warp / scale

    # Generate a cell seed
    sh.seed = sh.uv.x.floor() + sh.uv.y.floor() * scale

    # Pseudo-random color from the seed
    sh.red = (sh.seed * 12.9898).sin() * 43758.5453
    sh.green = (sh.seed * 78.233).sin() * 23421.631
    sh.blue = (sh.seed * 39.346).sin() * 12741.371

    sh.return_(sh.RgbF((
        sh.red - sh.red.floor(),
        sh.green - sh.green.floor(),
        sh.blue - sh.blue.floor(),
    )))

