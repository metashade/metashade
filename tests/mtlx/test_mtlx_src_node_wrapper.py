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

"""
Test for generating wrappers around MaterialX source-code nodes.

This test module verifies that Metashade can:
1. Discover source-code nodes via PyMaterialX
2. Generate wrapper functions that call the originals
3. Generate corresponding .mtlx implementation files
"""

import pytest

# Skip if MaterialX is not installed
mx = pytest.importorskip("MaterialX")

from metashade.mtlx.mtlx_reflection import (
    discover_acquirable_nodes,
    find_node_by_function,
    emit_wrapper_function,
    add_wrapper_impl,
    AcquireSrcCodeNode,
)
from metashade.mtlx.util.testing import GlslTestContext


class TestSrcNodeReflection:
    """Tests for discovering and inspecting source-code nodes."""
    
    @pytest.fixture
    def stdlib_doc(self) -> mx.Document:
        """Load the MaterialX standard library."""
        doc = mx.createDocument()
        search_path = mx.getDefaultDataSearchPath()
        mx.loadLibraries(mx.getDefaultDataLibraryFolders(), search_path, doc)
        return doc
    
    @pytest.fixture
    def all_nodes(self, stdlib_doc: mx.Document) -> list[AcquireSrcCodeNode]:
        """Discover all acquirable source-code nodes."""
        return discover_acquirable_nodes(stdlib_doc, target="genglsl")
    
    def test_discover_nodes_with_signatures(self, all_nodes: list[AcquireSrcCodeNode]):
        """Verify nodes are discovered with their full signatures."""
        assert len(all_nodes) > 50, f"Expected >50 nodes, found {len(all_nodes)}"
        
        # Each node should have outputs
        for node in all_nodes:
            assert len(node.outputs) > 0, f"Node {node.impl_name} has no outputs"
    
    def test_find_fractal3d_float(self, all_nodes: list[AcquireSrcCodeNode]):
        """Verify fractal3d_float can be found."""
        node = find_node_by_function(all_nodes, "mx_fractal3d_float")
        assert node is not None, "Could not find mx_fractal3d_float"


class TestSrcNodeWrapper:
    """Tests for generating wrapper code for source-code nodes."""
    
    @pytest.fixture
    def stdlib_doc(self) -> mx.Document:
        """Load the MaterialX standard library."""
        doc = mx.createDocument()
        search_path = mx.getDefaultDataSearchPath()
        mx.loadLibraries(mx.getDefaultDataLibraryFolders(), search_path, doc)
        return doc
    
    @pytest.fixture
    def fractal3d_node(self, stdlib_doc: mx.Document) -> AcquireSrcCodeNode:
        """Get the fractal3d_float node."""
        nodes = discover_acquirable_nodes(stdlib_doc, target="genglsl")
        node = find_node_by_function(nodes, "mx_fractal3d_float")
        assert node is not None
        return node
    
    def test_fractal3d_wrapper(self, fractal3d_node: AcquireSrcCodeNode):
        """Generate wrapper for fractal3d_float using Metashade generator."""
        ctx = GlslTestContext(base_name="mx_fractal3d_float_metashade", impl_only=True)
        
        with ctx as test_ctx:
            sh = test_ctx._sh
            
            # Generate the wrapper function
            emit_wrapper_function(sh, fractal3d_node)
            
            # Add MaterialX implementation
            test_ctx.add_node_impl(
                func_name="mx_fractal3d_float_metashade",
                mx_doc_string="Metashade wrapper for fractal3d_float"
            )
    
    def test_add_wrapper_impl_pymaterialx(self, fractal3d_node: AcquireSrcCodeNode):
        """Verify add_wrapper_impl creates proper PyMaterialX implementation."""
        doc = mx.createDocument()
        
        impl = add_wrapper_impl(doc, fractal3d_node)
        
        assert impl.getName() == "IM_fractal3d_float_genglsl_metashade"
        assert impl.getNodeDefString() == "ND_fractal3d_float"
        assert impl.getFile() == "mx_fractal3d_float_metashade.glsl"
        assert impl.getFunction() == "mx_fractal3d_float_metashade"
        assert impl.getTarget() == "genglsl"
