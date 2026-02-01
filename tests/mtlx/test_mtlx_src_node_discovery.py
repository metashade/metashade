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
Test for discovering MaterialX source-code nodes using PyMaterialX.

This test module:
1. Uses PyMaterialX to load stdlib/pbrlib definitions
2. Identifies "source-code nodes" (implementations with external GLSL files)
3. Prepares for wrapper generation that can wrap these nodes
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

# Skip if MaterialX is not installed
mx = pytest.importorskip("MaterialX")


@dataclass
class SourceCodeNode:
    """Represents a MaterialX source-code node implementation."""
    impl_name: str       # e.g., "IM_fractal3d_float_genglsl"
    nodedef_name: str    # e.g., "ND_fractal3d_float"
    glsl_file: str       # e.g., "mx_fractal3d_float.glsl"
    function_name: str   # e.g., "mx_fractal3d_float"


def get_stdlib_path() -> Path:
    """Get the path to MaterialX's standard library."""
    # Use MaterialX's built-in library path discovery
    search_path = mx.getDefaultDataSearchPath()
    # The library path is typically in the search path
    for path in search_path.asStringVec():
        lib_path = Path(path)
        if (lib_path / "stdlib").exists():
            return lib_path
    return None


def discover_source_code_nodes(doc: mx.Document) -> list[SourceCodeNode]:
    """
    Discover all source-code nodes for genglsl target.
    
    Source-code nodes are implementations that:
    - Target "genglsl"
    - Have a file attribute (external GLSL source)
    - Have a function attribute
    """
    nodes = []
    
    for impl in doc.getImplementations():
        # Only genglsl implementations
        if impl.getTarget() != "genglsl":
            continue
        
        # Only source-code implementations (have file + function)
        file_attr = impl.getAttribute("file")
        func_attr = impl.getAttribute("function")
        
        if file_attr and func_attr:
            nodedef = impl.getNodeDef()
            nodedef_name = nodedef.getName() if nodedef else impl.getNodeDefString()
            
            nodes.append(SourceCodeNode(
                impl_name=impl.getName(),
                nodedef_name=nodedef_name,
                glsl_file=file_attr,
                function_name=func_attr
            ))
    
    return nodes


class TestNodeDiscovery:
    """Tests for discovering MaterialX source-code nodes using PyMaterialX."""
    
    @pytest.fixture
    def stdlib_doc(self) -> mx.Document:
        """Load the MaterialX standard library."""
        doc = mx.createDocument()
        search_path = mx.getDefaultDataSearchPath()
        
        # Load stdlib
        mx.loadLibraries(mx.getDefaultDataLibraryFolders(), search_path, doc)
        
        return doc
    
    def test_stdlib_loads(self, stdlib_doc: mx.Document):
        """Verify we can load the MaterialX standard library."""
        # Should have nodedefs
        nodedefs = stdlib_doc.getNodeDefs()
        assert len(nodedefs) > 100, f"Expected >100 nodedefs, found {len(nodedefs)}"
    
    def test_has_implementations(self, stdlib_doc: mx.Document):
        """Verify the stdlib has implementations."""
        impls = stdlib_doc.getImplementations()
        assert len(impls) > 100, f"Expected >100 implementations, found {len(impls)}"
    
    def test_discover_source_code_nodes(self, stdlib_doc: mx.Document):
        """Discover all source-code nodes in stdlib."""
        nodes = discover_source_code_nodes(stdlib_doc)
        
        # Should find a significant number of source-code nodes
        assert len(nodes) > 50, f"Expected >50 source-code nodes, found {len(nodes)}"
        
        # Verify structure of discovered nodes
        for node in nodes:
            assert node.impl_name.startswith("IM_")
            assert node.glsl_file.endswith(".glsl")
            assert node.function_name  # Non-empty
    
    def test_discover_known_nodes(self, stdlib_doc: mx.Document):
        """Verify specific well-known nodes are discovered."""
        nodes = discover_source_code_nodes(stdlib_doc)
        
        # Build a set of function names for easy lookup
        func_names = {n.function_name for n in nodes}
        
        # These are known source-code nodes that should be found
        expected = [
            "mx_fractal3d_float",
            "mx_noise3d_float",
            "mx_worleynoise3d_float",
            "mx_image_float",
        ]
        
        for expected_func in expected:
            assert expected_func in func_names, f"Expected to find {expected_func}"
    
    def test_print_summary(self, stdlib_doc: mx.Document):
        """Print a summary of discovered nodes (for debugging)."""
        nodes = discover_source_code_nodes(stdlib_doc)
        
        print(f"\n=== Discovered {len(nodes)} source-code nodes ===")
        
        # Group by prefix (mx_noise, mx_fractal, etc.)
        by_prefix = {}
        for node in nodes:
            # Extract prefix like "mx_noise", "mx_fractal"
            parts = node.function_name.split("_")
            if len(parts) >= 2:
                prefix = f"{parts[0]}_{parts[1]}"
            else:
                prefix = node.function_name
            by_prefix.setdefault(prefix, []).append(node)
        
        for prefix, group in sorted(by_prefix.items()):
            print(f"  {prefix}: {len(group)} variants")
