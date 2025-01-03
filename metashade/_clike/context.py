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

import abc
import metashade._base.context as base

class FunctionDecl:
    '''
    Represents a function declaration in the target language.
    Meant to be created with a `sh.function` call. After creation,
    either call `declare()` to just declare it, without a definition,
    or use it in a `with` statement to implement the function body.
    '''
    def __init__(self, sh, name, return_type):
        self._sh = sh
        self._name = name
        self._return_type = (
            type(None) if ( return_type is None or return_type == type(None) )
            else return_type._get_dtype()
        )
        self._parameters = dict()

    def __getattr__(self, name):
        try:
            return self._parameters[name]
        except KeyError as e:
            raise AttributeError(e)

    def __call__(self, **kwargs):
        '''
        This doesn't generate a function call from external code.
        Instead, this initializes a part of the function signature -
        the declarations of parameters with their names and types.
        '''
        self._parameters = {
            name : arg_type() for name, arg_type in kwargs.items()
        }
        # Return self, so that it can be entered in a with scope
        return self

    def _declare_impl(self):
        # Context for the function arguments
        self._sh._push_context(self)

        return_type = (
            self._return_type._get_target_type_name()
            if self._return_type != type(None)
            else 'void'
        )

        # Emit the function signature
        self._sh._emit_indent()
        self._sh._emit(f'{return_type} {self._name}(')
        
        # Emit the argument declarations
        first = True
        for name, arg in self._parameters.items():
            if first:
                first = False
            else:
                self._sh._emit(', ')
            arg._define(self._sh, name, allow_init=False)

        self._sh._emit(')')

        # Register the callable in the generator
        self._sh._set_global(self._name, Function(self))

    def declare(self):
        self._declare_impl()
        self._sh._emit(';\n\n')
        self._sh._pop_context()

    def __enter__(self):
        self._declare_impl()
        self._sh._emit('\n{\n')
        self._sh._push_indent()
        
        # push and return the function body - a separate scope that can have
        # its own locals
        body = base.Scope()
        self._sh._push_context(body)
        return body
        
    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_context() # pop the function body
        self._sh._pop_context() # pop the function declaration
        self._sh._pop_indent()
        self._sh._emit('}\n\n')
    
    def return_(self, value=None):
        if ( (self._return_type is type(None) and value is not None)
            or not isinstance(value, self._return_type)
        ):
            raise RuntimeError('Return value type mismatch')

        self._sh._emit_indent()
        self._sh._emit('return{};\n'.format(
            ' ' + str(value) if value is not None else ''
        ))

class Function:
    '''
    A callable registered in the generator and referencing a function
    declaration.
    '''
    def __init__(self, definition : FunctionDecl) -> None:
        self._def = definition

    def __call__(self, **kwargs):
        arg_list = []

        for param_name, param in self._def._parameters.items():
            arg = kwargs.get(param_name)
            if param is None:
                raise RuntimeError(f'Parameter "{param_name}" missing')
            ref = param.__class__._get_value_ref(arg)
            if ref is None:
                raise RuntimeError(f'Parameter "{param_name}" type mismatch')
            
            arg_list.append(str(ref))
            kwargs.pop(param_name)

        if kwargs:
            raise RuntimeError(f'Missing arguments: {kwargs}')
        
        arg_str = ', '.join(arg_list)
        return self._def._return_type(f'{self._def._name}({arg_str})')
    
class _ConditionalStatement:
    def __init__(self, sh):
        self._sh = sh

    @abc.abstractmethod
    def _emit_statement(self):
        pass

    def __enter__(self):
        self._sh._emit_indent()
        self._emit_statement()
        self._sh._emit_indent()
        self._sh._emit('{\n')
        self._sh._push_indent()

        body = base.Scope()
        self._sh._push_context(body)
        return body

    def __exit__(self, exc_type, exc_value, traceback):
        self._sh._pop_context()
        self._sh._pop_indent()
        self._sh._emit_indent()
        self._sh._emit('}\n')

class If(_ConditionalStatement):
    def __init__(self, sh, condition):
        super().__init__(sh)
        self._condition = condition

    @abc.abstractmethod
    def _emit_statement(self):
        self._sh._emit(f'if ({self._condition})\n')

class Else(_ConditionalStatement):
    @abc.abstractmethod
    def _emit_statement(self):
        self._sh._emit('else\n')
