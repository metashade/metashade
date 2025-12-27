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

from metashade.util.testing import ctx_cls_hg, HlslTestContext
from metashade.modules import export

@export
def func_with_out(sh, out_val: "Out[Float]"):
    out_val._ = sh.Float(1.0)

@export
def func_with_inout(sh, inout_val: "InOut[Float]"):
    inout_val._ = inout_val + sh.Float(1.0)

class TestOutParams:
    @ctx_cls_hg
    def test_out_param_instantiation(self, ctx_cls):
        ctx = ctx_cls()
        with ctx as sh:
            sh.instantiate(func_with_out)

            with sh.entry_point('main')():
                sh.val = sh.Float(0.0)
                sh.func_with_out(out_val=sh.val)

    @ctx_cls_hg
    def test_inout_param_instantiation(self, ctx_cls):
        ctx = ctx_cls()
        with ctx as sh:
            sh.instantiate(func_with_inout)

            with sh.entry_point('main')():
                sh.val = sh.Float(1.0)
                sh.func_with_inout(inout_val=sh.val)
