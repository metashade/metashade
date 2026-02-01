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

from metashade.mtlx.dtypes import mtlx_to_metashade_dtype

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

def emit_extern_function(sh, node: AcquireSrcCodeNode):
    """
    Include the source file and declare the external function.
    
    This creates a callable Function object that can be used to generate
    calls to the MaterialX node implementation.
    
    Args:
        sh: The Metashade generator instance
        node: The source-code node to declare
        
    Returns:
        The callable Function object for this node
    """
    # Include the MaterialX source file
    sh.include(node.source_file)
    
    # Build parameter dict for function declaration
    params = {}
    for inp in node.inputs:
        dtype = mtlx_to_metashade_dtype(inp.mtlx_type, sh)
        if dtype is not None:
            params[inp.name] = dtype
    
    for out in node.outputs:
        dtype = mtlx_to_metashade_dtype(out.mtlx_type, sh)
        if dtype is not None:
            params[out.name] = sh.Out(dtype)
    
    # Declare the function (creates a callable Function object)
    sh.function(node.function_name)(**params).declare()
    
    # Return the callable
    return getattr(sh, node.function_name)

def emit_wrapper_function(sh, node: AcquireSrcCodeNode, suffix: str = "_metashade"):
    """
    Generate a wrapper function that calls the original MaterialX function.
    
    Args:
        sh: The Metashade generator instance
        node: The source-code node to wrap
        suffix: Suffix for the wrapper function name (default: "_metashade")
        
    Returns:
        The callable Function object for the wrapper
    """
    # First, emit the external function declaration
    extern_func = emit_extern_function(sh, node)
    
    wrapper_name = f"{node.function_name}{suffix}"
    
    # Build parameter dict (same as original)
    params = {}
    for inp in node.inputs:
        dtype = mtlx_to_metashade_dtype(inp.mtlx_type, sh)
        if dtype is not None:
            params[inp.name] = dtype
    
    for out in node.outputs:
        dtype = mtlx_to_metashade_dtype(out.mtlx_type, sh)
        if dtype is not None:
            params[out.name] = sh.Out(dtype)
    
    # Define the wrapper function
    with sh.function(wrapper_name)(**params):
        # Call the original function with all parameters
        call_args = {name: getattr(sh, name) for name in params}
        extern_func(**call_args)
    
    return getattr(sh, wrapper_name)

def add_wrapper_impl(doc, node: AcquireSrcCodeNode, suffix: str = "_metashade"):
    """
    Add a wrapper implementation to a MaterialX document using PyMaterialX.
    
    Args:
        doc: MaterialX Document to add to
        node: The source-code node being wrapped
        suffix: Suffix for wrapper names (default: "_metashade")
        
    Returns:
        The created Implementation object
    """
    wrapper_impl_name = f"{node.impl_name}{suffix}"
    wrapper_func_name = f"{node.function_name}{suffix}"
    wrapper_file = f"{wrapper_func_name}.glsl"
    
    impl = doc.addImplementation(wrapper_impl_name)
    impl.setNodeDefString(node.nodedef_name)
    impl.setFile(wrapper_file)
    impl.setFunction(wrapper_func_name)
    impl.setTarget(node.target)
    
    return impl
