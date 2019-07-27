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

class Struct(metashade.clike.data_types.BaseType):
    def __init__(self, struct_def):        
        super(Struct, self).__init__()
        
        self._struct_def = struct_def        
        for name, data_type in struct_def._member_defs.iteritems():
            setattr(self, name, data_type())
        
        self._constructed = True        
        
    def define(self, sh, identifier):
        super(Struct, self).define(sh, identifier)
        
        for member_name, member in vars(self).iteritems():
            if not member_name.startswith('_'):
                nested_name='{struct_name}.{member_name}'.format(
                    struct_name=identifier, member_name=member_name)
                member._bind(sh, nested_name, allow_defaults=False)           
        
    def get_target_type_name(self):
        return self._struct_def._identifier
    
    def __setattr__(self, name, value):
        if not name.startswith('_') and hasattr(self, '_constructed'):
            raise RuntimeError(
                "Metashade struct member can't be bound after construction")
            
        super(Struct, self).__setattr__(name, value)

class StructDef(object):
    def __init__(self, **kwargs):
        self._member_defs = kwargs
        
    def _get_generator(self):
        return self._sh
    
    """
    Called by the wrapping context.
    """
    def define(self, sh, identifier):
        self._identifier = identifier
        self._sh = sh._get_generator()
            
        self._sh._write('struct {identifier}\n{{\n'.format(
            identifier = self._identifier ))        
        self._sh._push_indent()
        
        first = True
        for member_name, member_type in self._member_defs.iteritems():
            if first:
                first = False
            else:
                self._sh._write(',\n')
            member_type.define_member(self._sh, member_name)
                        
        self._sh._pop_indent()
        self._sh._write('};\n\n')
        
    def __call__(self):
        return Struct(self)

    def is_type_of(self, value):
        return value._struct_def == self
