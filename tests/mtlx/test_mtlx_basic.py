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

import pytest

from metashade.mtlx.util.testing import GlslTestContext, OslTestContext

# OSL only adds implementations of the nodedefs written by the GLSL run.
_ctx_cls_go = pytest.mark.parametrize(
    'ctx_cls, impl_only',
    [(GlslTestContext, False), (OslTestContext, True)],
    ids=['glsl', 'osl']
)

class TestBasic:
    @_ctx_cls_go
    def test_dummy_purple(self, ctx_cls, impl_only):
        """Generate a simple purple color function."""
        ctx = ctx_cls(subdir='basic', impl_only=impl_only)
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            func_name = 'dummy_purple'
            
            # Define the purple function
            with sh.function(func_name)(result=sh.Out(sh.RgbF)):
                sh.result = sh.RgbF((0.5, 0.0, 1.0))
            
            # Add as MaterialX node
            test_ctx.add_node_impl(
                func_name=func_name,
                mx_doc_string='Metashade-generated dummy node that returns a purple color'
            )

    @_ctx_cls_go
    def test_metashade_add_color3(self, ctx_cls, impl_only):
        """Generate a color3 addition function."""
        ctx = ctx_cls(subdir='basic', impl_only=impl_only)
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            func_name = 'metashade_add_color3'
            
            # Define the color addition function
            with sh.function(func_name)(
                in1=sh.RgbF,
                in2=sh.RgbF,
                result=sh.Out(sh.RgbF)
            ):
                sh.result = sh.in1 + sh.in2
            
            # Add as MaterialX node
            test_ctx.add_node_impl(
                func_name=func_name,
                mx_doc_string='Metashade-generated node that adds two color3 values'
            )
