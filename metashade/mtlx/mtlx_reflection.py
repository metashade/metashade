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
MaterialX function acquisition for Metashade.

This module enables Metashade to acquire existing MaterialX source-code
functions, making them callable from Metashade-generated code.

Source-code functions are MaterialX implementations that have 'file' and
'function' attributes pointing to external GLSL/HLSL files, as opposed to
graph-based implementations defined in MaterialX XML.
"""

from metashade.mtlx.dtypes import mtlx_to_metashade_dtype
from metashade.targets._clike.context import FunctionDecl

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from metashade.targets._clike.context import Function

def _sanitize_identifier(name: str) -> str:
    """Sanitize an identifier to avoid reserved words.
    
    MaterialX commonly uses reserved keywords like 'in', 'out', and 'inout'
    as parameter names, which are reserved in GLSL/HLSL. This function
    appends an underscore to such identifiers.
    """
    reserved = {'out', 'in', 'inout'}
    if name in reserved:
        return name + '_'
    return name


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
    
    # Skip if already registered - duplicates occur because MaterialX has
    # stronger typing than GLSL/HLSL (e.g., color3 vs vector3 are both vec3)
    if hasattr(sh, func_attr):
        return getattr(sh, func_attr)
    
    # Build param annotations (inputs then outputs)
    param_annotations = {}
    
    for input in nodedef.getInputs():
        dtype = mtlx_to_metashade_dtype(input.getType(), sh)
        if dtype is None:
            raise TypeError(
                f"Cannot map MaterialX type '{input.getType()}' for input "
                f"'{input.getName()}' in {func_attr}"
            )
        param_name = _sanitize_identifier(input.getName())
        param_annotations[param_name] = dtype
    
    for output in nodedef.getOutputs():
        dtype = mtlx_to_metashade_dtype(output.getType(), sh)
        if dtype is None:
            raise TypeError(
                f"Cannot map MaterialX type '{output.getType()}' for output "
                f"'{output.getName()}' in {func_attr}"
            )
        param_name = _sanitize_identifier(output.getName())
        param_annotations[param_name] = sh.Out(dtype)
    
    # Declare the function without emitting code
    FunctionDecl(sh, func_attr, return_type=None)(
        **param_annotations
    ).declare(emit=False)
    
    return getattr(sh, func_attr)


def acquire_stdlib(sh, doc, target: str) -> dict[str, 'Function']:
    """
    Acquire all MaterialX source-code functions into the generator.
    
    After calling this, all MaterialX stdlib functions are available
    as callables on the generator (e.g., sh.mx_fractal3d_float(...)).
    
    Functions with unmappable types (e.g., string params) are skipped.
    
    Args:
        sh: The Metashade generator instance
        doc: A MaterialX Document with libraries loaded
        target: The codegen target (e.g., "genglsl", "genhlsl")
        
    Returns:
        Dict mapping function_name -> Function object
    """
    functions = {}
    
    for impl in doc.getImplementations():
        if impl.getTarget() != target:
            continue
        
        try:
            func = acquire_function(sh, impl)
            if func is not None:
                functions[func._name] = func
        except TypeError:
            # Skip functions with unmappable types (e.g., string params)
            pass
    
    return functions


def generate_wrapper_func(sh, impl, suffix: str = "_metashade"):
    """
    Generate a wrapper function for a MaterialX implementation.
    
    Includes the source file and generates a wrapper that calls
    the original function.
    
    Args:
        sh: The Metashade generator instance
        impl: A PyMaterialX nodeimpl object
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
    for input in nodedef.getInputs():
        dtype = mtlx_to_metashade_dtype(input.getType(), sh)
        if dtype is None:
            raise TypeError(
                f"Cannot map MaterialX type '{input.getType()}' for input "
                f"'{input.getName()}' in {wrapper_name}"
            )
        param_name = _sanitize_identifier(input.getName())
        params[param_name] = dtype
    
    for output in nodedef.getOutputs():
        dtype = mtlx_to_metashade_dtype(output.getType(), sh)
        if dtype is None:
            raise TypeError(
                f"Cannot map MaterialX type '{output.getType()}' for output "
                f"'{output.getName()}' in {wrapper_name}"
            )
        param_name = _sanitize_identifier(output.getName())
        params[param_name] = sh.Out(dtype)
    
    # Define the wrapper function
    with sh.function(wrapper_name)(**params):
        call_args = {name: getattr(sh, name) for name in params}
        orig_func(**call_args)
    
    return getattr(sh, wrapper_name)
