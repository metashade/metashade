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
from metashade.util.testing import ctx_cls_hg

class TestAugmentedAssignments:
    @ctx_cls_hg
    def test_augmented_add(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('assign_add', sh.Float4)(
                a = sh.Float4, b = sh.Float4
            ):
                sh.a += sh.b
                sh.return_(sh.a)

    @ctx_cls_hg
    def test_augmented_self_add(self, ctx_cls):
        """Test a += a (doubling) without using _ syntax."""
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('self_add', sh.Float4)(
                a = sh.Float4
            ):
                sh.a += sh.a
                sh.return_(sh.a)
