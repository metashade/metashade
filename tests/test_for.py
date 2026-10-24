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
from metashade.util.testing import ctx_cls_hg


class TestFor:
    @ctx_cls_hg
    def test_for_stop(self, ctx_cls):
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('sum_up_to', sh.Int)(n=sh.Int):
                sh.total = sh.Int(0)
                with sh.for_(i=sh.n):
                    sh.total += sh.i
                sh.return_(sh.total)

    @ctx_cls_hg
    def test_for_range_variants(self, ctx_cls):
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('range_variants', sh.Int)(n=sh.Int):
                sh.total = sh.Int(0)

                with sh.for_(i=4) as i:
                    assert i is sh.i
                    sh.total += i

                with sh.for_(i=(1, sh.n)):
                    sh.total += sh.i

                with sh.for_(i=range(0, 8, 2)):
                    sh.total += sh.i

                with sh.for_(i=(5, 0, -1)):
                    sh.total += sh.i

                with sh.for_(i=(10, 0, -2)):
                    sh.total += sh.i

                sh.return_(sh.total)

    @ctx_cls_hg
    def test_nested_for(self, ctx_cls):
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('nested_sum', sh.Int)(
                rows=sh.Int, cols=sh.Int
            ):
                sh.total = sh.Int(0)
                with sh.for_(r=sh.rows):
                    with sh.for_(c=sh.cols):
                        sh.total += sh.r * sh.cols + sh.c
                sh.return_(sh.total)

    @ctx_cls_hg
    def test_for_array(self, ctx_cls):
        with ctx_cls(dummy_entry_point=True) as sh:
            with sh.function('sum_array', sh.Float4)():
                sh.arr = sh.array(sh.Float4, (4,))()
                sh.total = sh.Float4(0.0)
                with sh.for_(i=4):
                    sh.total += sh.arr[sh.i]
                sh.return_(sh.total)

    @ctx_cls_hg
    def test_for_invalid_args(self, ctx_cls):
        with ctx_cls(no_file=True) as sh:
            with sh.function('invalid_for')(n=sh.Int):
                with pytest.raises(ValueError, match="exactly one keyword"):
                    with sh.for_():
                        pass

                with pytest.raises(ValueError, match="exactly one keyword"):
                    with sh.for_(i=4, j=4):
                        pass

                with pytest.raises(ValueError, match="must not be zero"):
                    with sh.for_(i=(0, 4, 0)):
                        pass

                with pytest.raises(ValueError, match="1, 2, or 3 elements"):
                    with sh.for_(i=(0, 1, 2, 3)):
                        pass

                with pytest.raises(TypeError, match="must be an int or Int"):
                    with sh.for_(i=1.5):
                        pass

                with pytest.raises(TypeError, match="must be an int or Int"):
                    with sh.for_(i=True):
                        pass

                with pytest.raises(TypeError, match="step must be an int"):
                    with sh.for_(i=(0, sh.n, sh.n)):
                        pass
