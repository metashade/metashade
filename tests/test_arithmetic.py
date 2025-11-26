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

class TestArithmetic:
    def _test_arithmetic(
            self,
            ctx_cls,
            scalar_type : str,
            vector2_type : str
    ):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function(
                'test_arithmetic', getattr(sh, vector2_type)
            )():
                sh.fD = getattr(sh, scalar_type)(-1)

                sh.f2A = getattr(sh, vector2_type)(0)
                sh.f2B = getattr(sh, vector2_type)((1, 2))
                
                sh.f2C = sh.f2A + sh.f2B
                sh.f2C += sh.f2B
                
                sh.f2C = sh.f2A - sh.f2B
                sh.f2C -= sh.f2B

                sh.f2C = sh.f2A * sh.f2B
                sh.f2C *= sh.f2B

                sh.f2C = sh.f2A / sh.f2B
                sh.f2C /= sh.f2B

                sh.f2C = sh.f2A * sh.fD
                sh.f2C *= sh.fD

                sh.f2C = sh.f2A / sh.fD
                sh.f2C /= sh.fD
                sh.return_(sh.f2C)

    @_base.ctx_cls_hg
    def test_arithmetic_float(self, ctx_cls):
        self._test_arithmetic(
            ctx_cls = ctx_cls,
            scalar_type = 'Float',
            vector2_type = 'Float2'
        )

    @_base.ctx_cls_hg
    def test_arithmetic_int(self, ctx_cls):
        self._test_arithmetic(
            ctx_cls = ctx_cls,
            scalar_type = 'Int',
            vector2_type = 'Int2'
        )



