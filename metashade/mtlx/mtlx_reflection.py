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

from __future__ import annotations

"""
MaterialX function acquisition for Metashade.

This module enables Metashade to acquire existing MaterialX source-code
functions, making them callable from Metashade-generated code.
"""

from metashade.mtlx.dtypes import mtlx_to_metashade_dtype
from metashade._clike.context import Function, _ParamDef
from metashade._rtsl.qualifiers import ParamQualifiers, Direction


def acquire_function(sh, impl):
    """
    Acquire a MaterialX function into the generator.
    
    Creates a callable Function object from a MaterialX Implementation,
    without emitting any code. The function can then be called to
    generate GLSL/HLSL calls.
    
    Args:
        sh: The Metashade generator instance
        impl: A PyMaterialX Implementation object
        
    Returns:
        The callable Function object, or None if not acquirable
    """
    file_attr = impl.getAttribute("file")
    func_attr = impl.getAttribute("function")
    
    if not (file_attr and func_attr):
        return None  # Not a source-code implementation
    
    nodedef = impl.getNodeDef()
    if nodedef is None:
        return None
    
    # Build param_defs in order (inputs then outputs)
    param_defs = {}
    
    for inp in nodedef.getInputs():
        dtype = mtlx_to_metashade_dtype(inp.getType(), sh)
        if dtype is None:
            continue
        param_defs[inp.getName()] = _ParamDef(
            dtype_factory=dtype,
            qualifiers=[]
        )
    
    for out in nodedef.getOutputs():
        dtype = mtlx_to_metashade_dtype(out.getType(), sh)
        if dtype is None:
            continue
        param_defs[out.getName()] = _ParamDef(
            dtype_factory=dtype,
            qualifiers=[ParamQualifiers(direction=Direction.OUT)]
        )
    
    # Skip if already registered (some impls share the same function)
    if hasattr(sh, func_attr):
        return getattr(sh, func_attr)
    
    # Create Function object and register without emitting
    func = Function(
        sh=sh,
        name=func_attr,
        return_type=None,  # MaterialX source functions return void
        param_defs=param_defs
    )
    sh._set_global(func_attr, func)
    
    return func


def acquire_stdlib(sh, doc, target: str = "genglsl") -> dict[str, Function]:
    """
    Acquire all MaterialX source-code functions into the generator.
    
    After calling this, all MaterialX stdlib functions are available
    as callables on the generator (e.g., sh.mx_fractal3d_float(...)).
    
    Args:
        sh: The Metashade generator instance
        doc: A MaterialX Document with libraries loaded
        target: The codegen target (default: "genglsl")
        
    Returns:
        Dict mapping function_name -> Function object
    """
    functions = {}
    
    for impl in doc.getImplementations():
        if impl.getTarget() != target:
            continue
        
        func = acquire_function(sh, impl)
        if func is not None:
            functions[func._name] = func
    
    return functions


def emit_wrapper(sh, impl, suffix: str = "_metashade"):
    """
    Generate a wrapper function for a MaterialX implementation.
    
    Includes the source file and generates a wrapper that calls
    the original function.
    
    Args:
        sh: The Metashade generator instance
        impl: A PyMaterialX Implementation object
        suffix: Suffix for the wrapper function name
        
    Returns:
        The wrapper Function object, or None if not wrappable
    """
    file_attr = impl.getAttribute("file")
    func_attr = impl.getAttribute("function")
    
    if not (file_attr and func_attr):
        return None
    
    nodedef = impl.getNodeDef()
    if nodedef is None:
        return None
    
    # Include the source file
    sh.include(file_attr)
    
    # Acquire the original function (no emission)
    orig_func = acquire_function(sh, impl)
    if orig_func is None:
        return None
    
    wrapper_name = f"{func_attr}{suffix}"
    
    # Build parameter dict for wrapper
    params = {}
    for inp in nodedef.getInputs():
        dtype = mtlx_to_metashade_dtype(inp.getType(), sh)
        if dtype is not None:
            params[inp.getName()] = dtype
    
    for out in nodedef.getOutputs():
        dtype = mtlx_to_metashade_dtype(out.getType(), sh)
        if dtype is not None:
            params[out.getName()] = sh.Out(dtype)
    
    # Define the wrapper function
    with sh.function(wrapper_name)(**params):
        call_args = {name: getattr(sh, name) for name in params}
        orig_func(**call_args)
    
    return getattr(sh, wrapper_name)


def add_wrapper_impl(doc, impl, suffix: str = "_metashade"):
    """
    Add a wrapper implementation to a MaterialX document.
    
    Args:
        doc: MaterialX Document to add to
        impl: The original Implementation being wrapped
        suffix: Suffix for wrapper names
        
    Returns:
        The created Implementation object, or None if not wrappable
    """
    func_attr = impl.getAttribute("function")
    if not func_attr:
        return None
    
    nodedef = impl.getNodeDef()
    if nodedef is None:
        return None
    
    wrapper_impl_name = f"{impl.getName()}{suffix}"
    wrapper_func_name = f"{func_attr}{suffix}"
    wrapper_file = f"{wrapper_func_name}.glsl"
    
    new_impl = doc.addImplementation(wrapper_impl_name)
    new_impl.setNodeDefString(nodedef.getName())
    new_impl.setFile(wrapper_file)
    new_impl.setFunction(wrapper_func_name)
    new_impl.setTarget(impl.getTarget())
    
    return new_impl
