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

from metashade.mtlx import julia_set
from metashade.mtlx.util.testing import GlslTestContext


def test_generate_julia_set():
    with GlslTestContext(
        base_name=julia_set.FUNC_NAME, subdir="julia_set"
    ) as ctx:
        julia_set.generate(ctx)
