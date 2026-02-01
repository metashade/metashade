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
MaterialX reflection utilities for discovering and wrapping source-code nodes.

This module provides tools to inspect MaterialX NodeDefs and Implementations
using PyMaterialX, enabling Metashade to "acquire" existing nodes.
"""

from dataclasses import dataclass
from typing import Optional

from metashade.mtlx.dtypes import mtlx_to_target_type

@dataclass
class SrcCodeNodeInput:
    """Represents an input parameter of a source-code node."""
    name: str
    mtlx_type: str
    default_value: Optional[str] = None

@dataclass
class SrcCodeNodeOutput:
    """Represents an output parameter of a source-code node."""
    name: str
    mtlx_type: str

@dataclass
class AcquireSrcCodeNode:
    """
    Represents a MaterialX source-code node that can be wrapped by Metashade.
    
    Contains all information needed to generate a wrapper function.
    """
    impl_name: str           # e.g., "IM_fractal3d_float_genglsl"
    nodedef_name: str        # e.g., "ND_fractal3d_float"
    source_file: str         # e.g., "mx_fractal3d_float.glsl"
    function_name: str       # e.g., "mx_fractal3d_float"
    target: str              # e.g., "genglsl"
    inputs: list[SrcCodeNodeInput]
    outputs: list[SrcCodeNodeOutput]

def get_nodedef_signature(nodedef) -> tuple[list[SrcCodeNodeInput], list[SrcCodeNodeOutput]]:
    """
    Extract typed inputs and outputs from a MaterialX NodeDef.
    
    Args:
        nodedef: A MaterialX NodeDef object
        
    Returns:
        Tuple of (inputs, outputs) lists
    """
    inputs = []
    for inp in nodedef.getInputs():
        inputs.append(SrcCodeNodeInput(
            name=inp.getName(),
            mtlx_type=inp.getType(),
            default_value=inp.getValueString() if inp.hasValueString() else None
        ))
    
    outputs = []
    for out in nodedef.getOutputs():
        outputs.append(SrcCodeNodeOutput(
            name=out.getName(),
            mtlx_type=out.getType()
        ))
    
    return inputs, outputs

def discover_acquirable_nodes(doc, target: str = "genglsl") -> list[AcquireSrcCodeNode]:
    """
    Discover all source-code nodes for a given target that can be acquired.
    
    Source-code nodes are implementations that:
    - Target the specified codegen target (e.g., "genglsl")
    - Have a file attribute (external source file)
    - Have a function attribute
    
    Args:
        doc: A MaterialX Document with libraries loaded
        target: The codegen target (default: "genglsl")
        
    Returns:
        List of AcquireSrcCodeNode objects with full signature info
    """
    nodes = []
    
    for impl in doc.getImplementations():
        if impl.getTarget() != target:
            continue
        
        file_attr = impl.getAttribute("file")
        func_attr = impl.getAttribute("function")
        
        if not (file_attr and func_attr):
            continue
        
        nodedef = impl.getNodeDef()
        if nodedef is None:
            continue
        
        inputs, outputs = get_nodedef_signature(nodedef)
        
        nodes.append(AcquireSrcCodeNode(
            impl_name=impl.getName(),
            nodedef_name=nodedef.getName(),
            source_file=file_attr,
            function_name=func_attr,
            target=target,
            inputs=inputs,
            outputs=outputs
        ))
    
    return nodes

def find_node_by_function(nodes: list[AcquireSrcCodeNode], function_name: str) -> Optional[AcquireSrcCodeNode]:
    """Find a node by its function name."""
    for node in nodes:
        if node.function_name == function_name:
            return node
    return None

def generate_wrapper_source(node: AcquireSrcCodeNode, target_dtypes_module, wrapper_suffix: str = "_metashade") -> str:
    """
    Generate wrapper source code for a source-code node.
    
    The wrapper includes the original file and defines a new function
    with the given suffix that simply calls the original.
    
    Args:
        node: The node to wrap
        target_dtypes_module: The target's dtypes module (e.g., metashade.glsl.dtypes)
        wrapper_suffix: Suffix for the wrapper function name (default: "_metashade")
        
    Returns:
        Source code string
    """
    wrapper_func_name = f"{node.function_name}{wrapper_suffix}"
    
    # Build parameter list
    params = []
    call_args = []
    
    for inp in node.inputs:
        target_type = mtlx_to_target_type(inp.mtlx_type, target_dtypes_module)
        if target_type is None:
            # Skip uniform/texture types for now
            continue
        params.append(f"{target_type} {inp.name}")
        call_args.append(inp.name)
    
    for out in node.outputs:
        target_type = mtlx_to_target_type(out.mtlx_type, target_dtypes_module)
        if target_type is None:
            continue
        params.append(f"out {target_type} {out.name}")
        call_args.append(out.name)
    
    params_str = ", ".join(params)
    call_args_str = ", ".join(call_args)
    
    # Generate the wrapper source
    source = f'''#include "{node.source_file}"

void {wrapper_func_name}({params_str})
{{
    {node.function_name}({call_args_str});
}}
'''
    return source

def generate_wrapper_mtlx_impl(node: AcquireSrcCodeNode, wrapper_suffix: str = "_metashade") -> str:
    """
    Generate MaterialX implementation XML for a wrapper node.
    
    Args:
        node: The node to wrap
        wrapper_suffix: Suffix for wrapper names (default: "_metashade")
        
    Returns:
        XML string for the implementation element
    """
    wrapper_func_name = f"{node.function_name}{wrapper_suffix}"
    wrapper_file = f"{node.function_name}{wrapper_suffix}.glsl"
    wrapper_impl_name = f"{node.impl_name}{wrapper_suffix}"
    
    return f'  <implementation name="{wrapper_impl_name}" nodedef="{node.nodedef_name}" file="{wrapper_file}" function="{wrapper_func_name}" target="{node.target}" />'
