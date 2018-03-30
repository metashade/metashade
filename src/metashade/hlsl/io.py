# Copyright 2018 Pavlo Penenko
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

import metashade.base.context
import metashade.clike.data_types

class ShaderInOut(metashade.clike.data_types.BaseType):
    def __init__(self, type_name):
        super(ShaderInOut, self).__init__()
        self._type_name = type_name
        
    def _target_name(self):
        return self._type_name

# TODO: perhaps this could be a metaclass?
class ShaderInOutDef(metashade.base.context.BaseContext):
    def __init__(self, **kwargs):
        self._members = {name : data_type() \
                         for name, data_type in kwargs.iteritems()}
                
    def define(self, sh, identifier):
        self._identifier = identifier
        self._parent = sh
        self._target = sh.get_target()
            
        self._target.write('struct {identifier}\n{{\n'.format(
            identifier = self._identifier ))        
        self._target.push_indent()
        
        first = True
        for name, member in self._members.iteritems():
            if first:
                first = False
            else:
                self._target.write(',\n')
            member.semantic_define(self, name)
                        
        self._target.pop_indent()
        self._target.write('};\n')
        
    def __call__(self):
        return ShaderInOut(self._identifier)

class VertexShaderIn(ShaderInOutDef):
    pass

class VertexShaderOut(ShaderInOutDef):
    pass