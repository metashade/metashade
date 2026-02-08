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

"""
Test for MaterialX function acquisition and wrapper generation.
"""

import pytest

# Skip if MaterialX is not installed
mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import (
    acquire_function,
    acquire_stdlib,
    generate_wrapper_func,
)
from metashade.mtlx.util.testing import GlslTestContext


class TestAcquireFunction:
    """Tests for acquiring MaterialX functions into Metashade."""
    
    def test_acquire_stdlib(self, stdlib_doc: mx.Document):
        """Verify we can acquire all stdlib functions."""
        from io import StringIO
        from metashade.glsl import frag
        
        # Create generator without file output
        out = StringIO()
        sh = frag.Generator(out, glsl_version='')
        
        functions = acquire_stdlib(sh, stdlib_doc, target="genglsl")
        
        assert len(functions) > 50, (
            f"Expected >50 functions, got {len(functions)}"
        )
        
        # Verify fractal3d_float was acquired
        assert "mx_fractal3d_float" in functions
        assert hasattr(sh, "mx_fractal3d_float")
    
    def test_acquire_single_function(self, stdlib_doc: mx.Document):
        """Test acquiring a single function."""
        from io import StringIO
        from metashade.glsl import frag
        
        # Create generator without file output
        out = StringIO()
        sh = frag.Generator(out, glsl_version='')
        
        # Find the fractal3d implementation
        impl = None
        for i in stdlib_doc.getImplementations():
            if i.getAttribute("function") == "mx_fractal3d_float":
                impl = i
                break
        
        assert impl is not None
        
        func = acquire_function(sh, impl)
        assert func is not None
        assert func._name == "mx_fractal3d_float"
        assert hasattr(sh, "mx_fractal3d_float")


class TestEmitWrapper:
    """Tests for generating wrapper functions."""
    
    @pytest.fixture
    def fractal3d_impl(self, stdlib_doc: mx.Document):
        """Get the fractal3d_float implementation."""
        for impl in stdlib_doc.getImplementations():
            if impl.getAttribute("function") == "mx_fractal3d_float":
                return impl
        pytest.fail("Could not find mx_fractal3d_float implementation")
    
    def test_generate_wrapper_func(self, fractal3d_impl):
        """Generate wrapper using Metashade generator."""
        ctx = GlslTestContext(
            base_name="mx_fractal3d_float_metashade", impl_only=True
        )
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            wrapper = generate_wrapper_func(sh, fractal3d_impl)
            assert wrapper is not None
            
            test_ctx.add_node_impl(
                func_name="mx_fractal3d_float_metashade",
                mx_doc_string="Metashade wrapper for fractal3d_float"
            )
