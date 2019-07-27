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

import metashade.base.context as base
from types import NoneType  
        
class Function(object):
    def __init__(self, **kwargs):
        super(Function, self).__init__(parent=None)
        
        self._args = dict()
        self._return_type = NoneType
        
        for name, arg_type in kwargs.iteritems():
            if name == 'return_type':
                self._return_type = arg_type
            else:
                self._args[name] = arg_type()
        
    def define(self, sh, identifier):
        self._identifier = identifier
        self._parent = sh
        self._sh = sh._get_generator()
        
        return_type = self._return_type().get_target_type_name() \
            if self._return_type != NoneType else 'void'
            
        self._sh._write('{return_type} {identifier}('.format(
            return_type = return_type,            
            identifier = self._identifier ))
        
        first = True
        for name, arg in self._args.iteritems():
            if first:
                first = False
            else:
                self._sh._write(', ')
            arg.arg_define(self, name)
                        
        self._sh._write(')\n')
        
    def __getattr__(self, name):
        arg = self._args.get(name)
        return arg if arg is not None \
            else super(function, self).__getattr__(name)
        
    def __enter__(self):
        self._sh._write('{\n')
        self._sh._push_indent()
        
        body = base.ScopedContext(parent=self)
        self._sh._push_context(body)        
        return body
        
    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_context()        
        self._sh._pop_indent()
        self._sh._write('}\n\n')
    
    def return_(self, value=None):
        mismatch_error = 'Return value type mismatch'        
        if self._return_type is NoneType:
            if value is not None:
                raise RuntimeError(mismatch_error)
        else:                
            if not self._return_type.is_type_of(value):
                raise RuntimeError(mismatch_error)            
            
        self._sh._write('return{};\n'.format(
            ' ' + value.get_ref() if value is not None else ''))
