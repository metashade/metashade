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
Type mappings between Metashade and MaterialX.
"""

# Canonical map from Metashade dtype class names to MaterialX type strings
_METASHADE_TO_MTLX = {
    'Float': 'float',
    'Int': 'integer',
    'RgbF': 'color3',
    'RgbaF': 'color4',
    'Float2': 'vector2',
    'Float3': 'vector3',
    'Float4': 'vector4',
    'Float3x3': 'matrix33',
    'Float4x4': 'matrix44',
}

# Derive the inverse map from the canonical forward map
_MTLX_TO_METASHADE = {v: k for k, v in _METASHADE_TO_MTLX.items()}

# Add MaterialX type aliases (not in forward map, but valid MaterialX types)
_MTLX_TO_METASHADE.update({
    'int': 'Int',  # Alias for 'integer'
})

# Types that don't have Metashade equivalents (for documentation)
_UNSUPPORTED_MTLX_TYPES = frozenset({
    'boolean',      # No direct Metashade equivalent yet
    'string',       # Uniform metadata, not in function signatures
    'filename',     # Texture references
    'integerarray', # Arrays need special handling
    'floatarray',
})


def metashade_to_mtlx(dtype_factory):
    """Map a Metashade dtype factory to a MaterialX type string."""
    if dtype_factory is None:
        return None
    
    dtype = dtype_factory._get_dtype()
    dtype_name = dtype.__name__
    
    if dtype_name not in _METASHADE_TO_MTLX:
        raise ValueError(
            f"No MaterialX type mapping for Metashade dtype '{dtype_name}'"
        )
    
    return _METASHADE_TO_MTLX[dtype_name]


def mtlx_to_target_type(mtlx_type: str, target_dtypes_module) -> str | None:
    """
    Convert a MaterialX type to a target language type name.
    
    Args:
        mtlx_type: MaterialX type string (e.g., 'float', 'vector3')
        target_dtypes_module: The target's dtypes module
        
    Returns:
        Target language type name (e.g., 'float', 'vec3') or None
    """
    metashade_name = _MTLX_TO_METASHADE.get(mtlx_type)
    if metashade_name is None:
        return None
    
    dtype_class = getattr(target_dtypes_module, metashade_name, None)
    if dtype_class is None:
        return None
    
    return getattr(dtype_class, '_target_name', metashade_name.lower())


def mtlx_to_metashade_dtype(mtlx_type: str, sh):
    """
    Get the Metashade dtype factory for a MaterialX type.
    
    Args:
        mtlx_type: MaterialX type string (e.g., 'float', 'vector3')
        sh: The Metashade generator instance
        
    Returns:
        Dtype factory (e.g., sh.Float, sh.Float3) or None if not mappable
    """
    metashade_name = _MTLX_TO_METASHADE.get(mtlx_type)
    if metashade_name is None:
        return None
    
    return getattr(sh, metashade_name, None)
