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
