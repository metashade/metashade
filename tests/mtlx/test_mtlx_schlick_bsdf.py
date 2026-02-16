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

from __future__ import annotations

import pytest

# Skip if MaterialX is not installed
mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import (
    generate_wrapper_func,
)
from metashade.mtlx.dtypes import register_mtlx_closure_structs
from metashade.mtlx.util.testing import GlslTestContext


class TestSchlickBsdfWrapper:
    """Tests for generating wrapper for generalized_schlick_bsdf."""
    
    @pytest.fixture
    def schlick_impl(self, stdlib_doc: mx.Document):
        """Get the localized implementation for generalized_schlick_bsdf."""
        # Find implementation for "genglsl" target
        for impl in stdlib_doc.getImplementations():
            if (
                impl.getNodeDefString().endswith("generalized_schlick_bsdf") and
                impl.getTarget() == "genglsl"
            ):
                return impl
        
        # Fallback: try searching by nodedef name directly if possible, or just print what we have
        # But 'ending with' is safer because names can have prefixes
        pytest.fail("Could not find genglsl implementation for generalized_schlick_bsdf")

    def test_generate_schlick_wrapper(self, schlick_impl):
        """
        Generate a wrapper implementation for generalized_schlick_bsdf.
        
        This verifies we can acquire the standard node and re-emit it 
        as a Metashade-managed implementation (Phase 2 acquisition).
        """
        # Use a distinctive base name for the output files
        ctx = GlslTestContext(
            base_name="mx_generalized_schlick_bsdf_metashade", 
            impl_only=True
        )
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            # Declare standard MaterialX closure structs
            register_mtlx_closure_structs(sh)
            
            # 1. Generate the wrapper function in Metashade
            wrapper = generate_wrapper_func(sh, schlick_impl)
            
            assert wrapper is not None
            assert hasattr(sh, wrapper._name)
            
            # 2. Register this wrapper as an implementation for the ORIGINAL nodedef
            # This is the "overload" part - providing a new implementation for ND_generalized_schlick_bsdf
            test_ctx.add_node_impl(
                func_name=wrapper._name,
                mx_doc_string="Metashade wrapper for generalized_schlick_bsdf",
                nodedef_name="ND_generalized_schlick_bsdf"
            )
