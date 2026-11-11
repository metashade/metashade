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

import pytest

pytest.importorskip("MaterialX")

from metashade.mtlx.util.testing import GlslTestContext, OslTestContext
from metashade.std.procedural import noisy_squares


# OSL only adds implementations of the nodedefs written by the GLSL run.
@pytest.mark.parametrize(
    'ctx_cls, impl_only',
    [(GlslTestContext, False), (OslTestContext, True)],
    ids=['glsl', 'osl']
)
def test_noisy_squares2d(ctx_cls, impl_only):
    with ctx_cls(subdir='noisy_squares2d', impl_only=impl_only) as ctx:
        ctx.add_std_pyfunc_node_impl(
            noisy_squares.noisy_squares2d, nodegroup='procedural2d'
        )
