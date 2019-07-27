# Copyright 2017 Pavlo Penenko
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

import metashade.base.data_types as base
import metashade.slang.data_types as slang

class SemanticMixin(base.BaseType):
    @classmethod
    def define_member(cls, target, identifier):        
        target._write('{type_name} {identifier} : {semantic};\n'.format(
            type_name = cls._target_name,
            identifier = identifier,
            semantic = cls._semantic ))

class Float(slang.Float):
    _target_name = 'float'
    
class Point3f(slang.Point3f, SemanticMixin):
    _target_name = 'float3'
    _semantic = 'POSITION'
    
class Vector4f(slang.Vector4f, SemanticMixin):
    def __init__(self, xyzw = None):
        initializer=None if xyzw is None else \
            'float4({0}, {1}, {2}, {3})'.format(*xyzw)                
        super(Vector4f, self).__init__(initializer)            
                
    _target_name = 'float4'
    _semantic = 'POSITION'
    
class RGBA(slang.RGBA, SemanticMixin):
    def __init__(self, rgba = None):
        initializer=None if rgba is None else \
            'float4({0}, {1}, {2}, {3})'.format(*rgba)                
        super(RGBA, self).__init__(initializer)
    
    _target_name = 'float4'
    _semantic = 'COLOR'
