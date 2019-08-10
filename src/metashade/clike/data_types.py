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

class BaseType(base.BaseType):
    def define(self, sh, identifier):
        self._bind(sh, identifier, allow_defaults=True)
        
        self._sh._write('{type_name} {identifier}{initializer};\n'.format(
            type_name = self.get_target_type_name(),
            identifier = self._identifier,
            initializer = '' if self._value is None else ' = {}'.format(self._value) ))
        
    def arg_define(self, function, identifier):
        self._bind(function, identifier, allow_defaults=False)
        
        self._sh._write('{type_name} {identifier}'.format(
            type_name = self.get_target_type_name(),
            identifier = self._identifier))
        
    def __setattr__(self, name, value):
        if name == '_':
            self._value = value
            self._sh._write('{identifier} = {value};\n'.format(
                identifier = self._identifier,
                value = value.get_ref() if hasattr(value, 'get_ref') else value ))
        else:
            object.__setattr__(self, name, value)
            
    def get_target_type_name(self):
        return self.__class__._target_name
            
class AddMixIn(object):
    def __add__(self, rhs):
        return self.__class__('{this} + {rhs}'.format(
            this = self.get_ref(), rhs = rhs.get_ref() ))
        
class Float(BaseType, AddMixIn):
    pass