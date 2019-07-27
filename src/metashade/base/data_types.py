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

class BaseType(object):
    """
    The base class for all Metashade types.
    """    
    def __init__(self, initializer = None):
        self._identifier = None
        self._value = initializer
        
    def _bind(self, scope, identifier, allow_defaults):
        if not allow_defaults and self._value is not None:
            raise RuntimeError('Arguments with default values are not supported.')
        
        self._identifier = identifier
        self._sh = scope._get_generator()
        #self._is_arg = is_arg
        
    def get_ref(self):
        if self._identifier is not None:            
            #TODO: re-enable when struct members are sorted out
            #if not self._is_arg and self._value is None:
            #    raise RuntimeError(
            #        'Variable is used before it has been assigned a value')
            
            return self._identifier
        
        elif self._value is not None:
            return self._value
        else:        
            raise RuntimeError('Instance is neither a variable nor expression.')
        
    @classmethod
    def is_type_of(cls, value):
        return isinstance(value, cls)