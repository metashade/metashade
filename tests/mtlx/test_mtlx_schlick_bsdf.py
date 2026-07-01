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


@pytest.fixture
def schlick_impl(stdlib_doc: mx.Document):
    """Get the genglsl implementation for generalized_schlick_bsdf."""
    for impl in stdlib_doc.getImplementations():
        if (
            impl.getNodeDefString().endswith("generalized_schlick_bsdf") and
            impl.getTarget() == "genglsl"
        ):
            return impl
    pytest.fail("Could not find genglsl implementation for generalized_schlick_bsdf")


class TestSchlickBsdfPassthru:
    """Passthru wrapper: calls the original Schlick unchanged."""

    def test_generate_schlick_passthru(self, schlick_impl):
        """
        Generate a passthru wrapper implementation for generalized_schlick_bsdf.
        
        This verifies we can acquire the standard node and re-emit it 
        as a Metashade-managed implementation (Phase 2 acquisition).
        """
        # Use a distinctive base name for the output files
        ctx = GlslTestContext(
            base_name="mx_generalized_schlick_bsdf_metashade", 
            impl_only=True,
            subdir="source_code_node_passthrus"
        )
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            # Declare standard MaterialX closure structs
            register_mtlx_closure_structs(sh)
            
            # Generate the wrapper function in Metashade
            wrapper = generate_wrapper_func(sh, schlick_impl)
            
            assert wrapper is not None
            assert hasattr(sh, wrapper._name)
            
            # Register this wrapper as an implementation for the ORIGINAL nodedef
            test_ctx.add_node_impl(
                func_name=wrapper._name,
                mx_doc_string="Metashade passthru wrapper for generalized_schlick_bsdf",
                nodedef_name="ND_generalized_schlick_bsdf"
            )


class TestSchlickBsdfBroken:
    """Broken Schlick: returns hot pink, proving the override pipeline works."""

    def test_generate_broken_schlick(self, schlick_impl):
        """
        Generate a deliberately broken Schlick that returns hot pink.
        
        Uses the body callback to override the default passthru behavior,
        validating both the callback mechanism and the subdir scoping.
        """
        def broken_body(sh, orig_func):
            sh.out_.response = [1.0, 0.0, 0.5]
            sh.out_.throughput = [0.0, 0.0, 0.0]

        ctx = GlslTestContext(
            base_name="mx_generalized_schlick_bsdf_broken",
            impl_only=True,
            subdir="broken_schlick"
        )
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            register_mtlx_closure_structs(sh)
            
            wrapper = generate_wrapper_func(
                sh, schlick_impl,
                suffix="_broken",
                body=broken_body
            )
            
            assert wrapper is not None
            
            test_ctx.add_node_impl(
                func_name=wrapper._name,
                mx_doc_string="Broken Schlick: returns hot pink to validate override pipeline",
                nodedef_name="ND_generalized_schlick_bsdf"
            )
