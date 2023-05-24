# Copyright 2019 Pavlo Penenko
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

import metashade.clike.struct as struct

'''
    See https://docs.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-semantics
'''

class SemanticDef:
    def __init__(self, allow_multi):
        self.allow_multi = allow_multi

class StageInterfaceDefMeta(type):
    def __init__(cls, name, bases, member_dict):
        super().__init__(name, bases, member_dict)

        def create_semantic_func(semantic_name, semantic_def):
            def semantic_func(self, attribute_name, dtype_factory):
                self._add_attribute(
                    attribute_name,
                    semantic_name,
                    semantic_def,
                    dtype_factory._dtype
                )

            return semantic_func

        for semantic_name, semantic_def in cls._semantic_defs.items():
            semantic_func = create_semantic_func(semantic_name, semantic_def)
            setattr(cls, semantic_name, semantic_func)

class StageInterfaceDef:
    def __init__(self, sh, name):
        self._sh = sh
        self._name = name
        self._semantic_counts = \
            { name : 0 for name in self.__class__._semantic_defs.keys()}
        self._attributes = dict()   # name to semantic

    def __enter__(self):
        return self

    def _add_attribute(self, name, semantic_name, semantic_def, dtype):
        self._semantic_counts[semantic_name] += 1

        if (self._semantic_counts[semantic_name] > 1
            and not semantic_def.allow_multi
        ):
            raise RuntimeError(
                f"Only one instance of semantic {semantic_name} "
                "is allowed in an interface block"
            )

        self._attributes[name] = struct.StructMemberDef(dtype, semantic_name)

    def __exit__(self, exc_type, exc_value, traceback):
        member_defs = dict()
        semantic_indices = \
            { name : -1 for name in self.__class__._semantic_defs.keys()}

        for attribute_name, attribute_def in self._attributes.items():
            semantic_indices[attribute_def.semantic] += 1
            semantic_index = semantic_indices[attribute_def.semantic]

            semantic_name = attribute_def.semantic.upper()
            if semantic_index > 0 \
                or self._semantic_counts[attribute_def.semantic] > 1:
                semantic_name += str(semantic_index)

            member_defs[attribute_name] = struct.StructMemberDef(
                attribute_def.dtype, semantic_name
            )

        struct.define_struct(self._sh, self._name, member_defs)

class VsInputDef(StageInterfaceDef, metaclass = StageInterfaceDefMeta):
    _semantic_defs = {
        'binormal'      : SemanticDef(True),    # Binormal, float4
        'blendIndices'  : SemanticDef(True),    # Blend indices, uint
        'blendWeight'   : SemanticDef(True),    # Blend weights, float
        'color'         : SemanticDef(True),    # Diffuse and specular color,	float4
        'normal'        : SemanticDef(True),    # Normal vector,	float4
        'position'      : SemanticDef(True),    # Vertex position in object space,	float4
        'positionT'     : SemanticDef(False),   # Transformed vertex position,	float4
        'pSize'         : SemanticDef(True),    # Point size,	float
        'tangent'       : SemanticDef(True),    #Tangent,	float4
        'texCoord'      : SemanticDef(True)     # Texture coordinates,	float4
    }

class VsOutputDef(StageInterfaceDef, metaclass = StageInterfaceDefMeta):
    _semantic_defs = {
        'color'     : SemanticDef(True),    # Diffuse or specular color,	float4
        'fog'       : SemanticDef(False),   # Vertex fog,   float
        'SV_Position' : SemanticDef(True),  # Position of a vertex in homogenous space, float4
        'pSize'     : SemanticDef(False),   # Point size,	float
        'tessFactor': SemanticDef(True),    # Tessellation factor,	float
        'texCoord'  : SemanticDef(True),    # Texture coordinates,	float4
    }

# TODO: PS inputs distinct from VS outputs

class PsOutputDef(StageInterfaceDef, metaclass = StageInterfaceDefMeta):
    _semantic_defs = {
        'SV_Target' : SemanticDef(True),    # Output color,	float4
        'SV_Depth'  : SemanticDef(True),    # Output depth,	float
    }