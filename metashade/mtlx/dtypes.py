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

def metashade_to_mtlx(dtype_factory):
    '''Map a Metashade dtype factory to a MaterialX type string.'''
    if dtype_factory is None:
        return None
    
    dtype = dtype_factory._get_dtype()
    dtype_name = dtype.__name__
    
    # Map Metashade types to MaterialX types
    type_map = {
        'Float': 'float',
        'RgbF': 'color3',
        'RgbaF': 'color4',
        'Float2': 'vector2',
        'Float3': 'vector3',
        'Float4': 'vector4',
        'Float3x3': 'matrix33',
        'Float4x4': 'matrix44',
    }
    
    if dtype_name not in type_map:
        raise ValueError(
            f"No MaterialX type mapping for Metashade dtype '{dtype_name}'"
        )
    
    return type_map[dtype_name]


# Map MaterialX types to Metashade dtype class names
# This is the reverse of metashade_to_mtlx
MTLX_TO_METASHADE_NAME = {
    'float': 'Float',
    'integer': 'Int',
    'boolean': None,  # No direct Metashade equivalent yet
    'vector2': 'Float2',
    'vector3': 'Float3',
    'vector4': 'Float4',
    'color3': 'RgbF',
    'color4': 'RgbaF',
    'matrix33': 'Float3x3',
    'matrix44': 'Float4x4',
    'string': None,  # Uniforms, not in function signature
    'filename': None,  # Texture references
    'integerarray': None,  # Arrays need special handling
    'floatarray': None,
}


def mtlx_to_target_type(mtlx_type: str, target_dtypes_module) -> str | None:
    """
    Convert a MaterialX type to a target language type name.
    
    Args:
        mtlx_type: MaterialX type string (e.g., 'float', 'vector3', 'color3')
        target_dtypes_module: The target's dtypes module (e.g., metashade.glsl.dtypes)
        
    Returns:
        Target language type name (e.g., 'float', 'vec3') or None if not mappable
    """
    metashade_name = MTLX_TO_METASHADE_NAME.get(mtlx_type)
    if metashade_name is None:
        return None
    
    dtype_class = getattr(target_dtypes_module, metashade_name, None)
    if dtype_class is None:
        return None
    
    # Get the target-specific type name
    return getattr(dtype_class, '_target_name', metashade_name.lower())

