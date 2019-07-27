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

import data_types
import context

class Generator(object):
    """
    The base class for generators. Wraps an output file.
    """
    def __init__(self, file_):
        self._file = file_
        
        self._indent = 0
        self._indent_char = '\t'
        self._indent_delta = 1
        
        self._context_stack = list()
        
    def _get_generator(self):
        return self
    
    def _push_indent(self):
        self._indent += self._indent_delta
        
    def _pop_indent(self):
        self._indent -= self._indent_delta
        
    def _get_indent(self):
        return self._indent_char * (self._indent * self._indent_delta)
    
    def _write(self, line):
        self._file._write(self._get_indent() + line)
        
    def _push_context(self, context):
        self._context_stack.append(context)
        
    def _pop_context(self):
        self._context_stack.pop()            

    def __getattr__(self, name):        
        return getattr(self._context_stack[-1], name)
    
    def __setattr__(self, name, value):
        if name.startswith('_'): #private variables are never meta
            object.__setattr__(self, name, value)
        else:
            if self.__dict__.get('_context_stack'):
                setattr(self._context_stack[-1], name, value)
            else:
                super(Generator, self).__setattr__(name, value)            
