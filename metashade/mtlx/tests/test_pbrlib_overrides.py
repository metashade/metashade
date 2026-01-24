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
Tests for generating Metashade overrides of MaterialX pbrlib nodes.

These tests generate <implementation> elements that override existing
MaterialX nodedefs with Metashade-generated shader code.
"""

from metashade_mtlx.util.testing import GlslTestContext
from metashade_mtlx.pbrlib import generalized_schlick_bsdf


class TestPbrlibOverrides:
    """Tests for generating pbrlib node overrides.
    
    Generates library-level files:
    - metashade_pbrlib_genglsl_impl.mtlx (all impl elements)
    - metashade_pbrlib_genglsl_impl.glsl (all GLSL functions)
    """
    
    def test_pbrlib_overrides(self):
        """Generate Metashade overrides for all pbrlib nodes.
        
        This generates library-level files:
        - metashade_pbrlib_genglsl_impl.mtlx
        - metashade_pbrlib_genglsl_impl.glsl
        
        Multiple functions are added to the same files.
        """
        ctx = GlslTestContext(
            base_name='metashade_pbrlib',
            impl_only=True
        )
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            # generalized_schlick_bsdf
            sh.instantiate(
                generalized_schlick_bsdf.mx_metashade_generalized_schlick_bsdf
            )
            # Add as override implementation for existing MaterialX nodedef
            test_ctx.add_node_impl(
                func_name='mx_metashade_generalized_schlick_bsdf',
                mx_doc_string='Metashade override of generalized_schlick_bsdf',
                nodedef_name='ND_generalized_schlick_bsdf'
            )
            
            # Add more node overrides here as they are implemented:
            # sh.instantiate(dielectric_bsdf.mx_metashade_dielectric_bsdf)
            # test_ctx.add_impl_override(...)
