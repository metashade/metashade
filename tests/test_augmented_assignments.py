# Copyright 2023 Pavlo Penenko
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
import _base

class TestAugmentedAssignments(_base.TestBase):
    @pytest.mark.parametrize(
        'ctx_cls', [_base.HlslTestContext, _base.GlslTestContext]
    )
    def test_augmented_add(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('assign_add', sh.Float4)(
                a = sh.Float4, b = sh.Float4
            ):
                sh.a += sh.b
                sh.return_(sh.a)
