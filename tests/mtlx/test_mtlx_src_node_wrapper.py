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

import os
from pathlib import Path

import pytest

# Skip if MaterialX is not installed
mx = pytest.importorskip("MaterialX")

from metashade.util.testing import RefDiffer
from metashade.mtlx.mtlx_reflection import (
    discover_acquirable_nodes,
    find_node_by_function,
    generate_wrapper_source,
    generate_wrapper_mtlx_impl,
    AcquireSrcCodeNode,
)

# Output/reference directories (same pattern as other tests)
_parent_dir = Path(__file__).parent.parent
_ref_dir = _parent_dir / "ref" / "mtlx"

_out_dir_env = os.getenv('METASHADE_PYTEST_OUT_DIR', None)
if _out_dir_env is None:
    _out_dir = _ref_dir
    _ref_differ = None
else:
    _out_dir = Path(_out_dir_env).resolve() / "mtlx"
    _ref_differ = RefDiffer(_ref_dir)

os.makedirs(_out_dir, exist_ok=True)


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
        """Generate wrapper for fractal3d_float and compare to reference."""
        # Generate wrapper content
        glsl_source = generate_wrapper_source(fractal3d_node)
        mtlx_impl = generate_wrapper_mtlx_impl(fractal3d_node)
        
        # Create combined MTLX document
        mtlx_content = f'''<?xml version="1.0"?>
<materialx version="1.39">
{mtlx_impl}
</materialx>
'''
        
        # Save to output directory
        glsl_path = _out_dir / "mx_fractal3d_float_metashade.glsl"
        mtlx_path = _out_dir / "metashade_fractal3d_genglsl_impl.mtlx"
        
        glsl_path.write_text(glsl_source)
        mtlx_path.write_text(mtlx_content)
        
        # Compare to reference in CI
        if _ref_differ is not None:
            _ref_differ(glsl_path)
            _ref_differ(mtlx_path)
