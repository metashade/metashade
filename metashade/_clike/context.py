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
import typing
from typing import NamedTuple

import metashade._base.context as base
from .._rtsl.qualifiers import ParamQualifiers

class _ParamDef(NamedTuple):
    '''
    Function parameter definition: dtype factory and qualifiers.
    '''
    dtype_factory: object  # Generator._DtypeFactory
    qualifiers: list  # List of ParamQualifiers

class FunctionDecl:
    '''
    Represents a function declaration in the target language.
    Created with `sh.function`. Call `declare()` for a prototype,
    or use in a `with` statement to define the function body.
    
    Short-lived object that creates a persistent Function object.
    '''
    def __init__(self, sh, name, return_type, doc = None):
        self._sh = sh
        self._name = name
        self._return_dtype_factory = (
            None if ( return_type is None or return_type == type(None) )
            else return_type
        )
        self._doc = doc
        self._param_defs = dict()

    def __call__(self, **kwargs):
        '''Initialize the function signature.'''
        return self._init_param_defs(**kwargs)

    def _init_param_defs(self, **param_annotations):
        '''Parse parameter annotations to extract dtype factories and qualifiers.'''
        self._param_defs = {}
        
        for name, dtype_factory in param_annotations.items():
            # Check if this is an Annotated type with qualifiers
            qualifiers = []
            if typing.get_origin(dtype_factory) is typing.Annotated:
                # Extract base dtype factory and qualifiers from 
                # Annotated[dtype_factory, qualifier1, qualifier2, ...]
                typing_args = typing.get_args(dtype_factory)
                dtype_factory = typing_args[0]
                qualifiers = [
                    annotation for annotation in typing_args[1:]
                    if isinstance(annotation, ParamQualifiers)
                ]
            
            self._param_defs[name] = _ParamDef(
                dtype_factory=dtype_factory,
                qualifiers=qualifiers
            )

        # Return self, so that it can be entered in a with scope
        return self

    def _emit_signature(self):
        '''Emit the function signature.'''
        return_type = (
            self._return_dtype_factory._get_dtype()._get_target_type_name()
            if self._return_dtype_factory is not None
            else 'void'
        )

        # Emit the function signature
        self._sh._emit_indent()
        self._sh._emit(f'{return_type} {self._name}(')
        
        # Emit the argument declarations
        first = True
        for name, param_def in self._param_defs.items():
            if first:
                first = False
            else:
                self._sh._emit(', ')

            # Create a temporary instance using the dtype factory
            param_instance = param_def.dtype_factory()
            param_instance._define(
                self._sh,
                name,
                allow_init=False,
                qualifiers=param_def.qualifiers
            )

        self._sh._emit(')')

    def declare(self):
        '''Emit a function prototype.'''
        self._sh._emit_line_directive()
        self._emit_signature()
        self._sh._emit(';\n\n')
        
        # Register the callable in the generator
        self._sh._set_global(
            self._name,
            Function(
                sh=self._sh,
                name=self._name,
                return_type=self._return_dtype_factory,
                param_defs=dict(self._param_defs)
            )
        )

    def __enter__(self):
        '''Begin function definition and return a FunctionDef for the body.'''
        if self._doc is not None:
            for line in self._doc.strip().split('\n'):
                # Escape non-ASCII characters to \uXXXX format for safe output
                safe_line = line.strip().encode('ascii', 'backslashreplace').decode('ascii')
                self._sh._emit_indent()
                self._sh._emit(f'// {safe_line}\n')
            self._sh._emit_indent()
            self._sh._emit('//\n')

        self._sh._emit_line_directive()
        self._emit_signature()
        self._sh._emit('\n{\n')
        self._sh._push_indent()
        
        # Create and return a FunctionDef to manage the function body
        func_def = FunctionDef(
            sh=self._sh,
            name=self._name,
            return_type=self._return_dtype_factory,
            param_defs=self._param_defs
        )
        
        # Register the callable in the generator
        self._sh._set_global(
            self._name,
            Function(
                sh=self._sh,
                name=self._name,
                return_type=self._return_dtype_factory,
                param_defs=dict(self._param_defs)
            )
        )
        
        return func_def
        
    def __exit__(self, exc_type, exc_value, traceback):
        '''Complete the function definition.'''
        self._sh._pop_context()  # pop the function body scope
        self._sh._pop_context()  # pop the FunctionDef (parameters)
        self._sh._pop_indent()
        self._sh._emit('}\n\n')

class FunctionDef:
    '''
    Manages the function body scope. Provides access to parameters
    and the return_ method. Short-lived, exists during definition.
    '''
    def __init__(self, sh, name, return_type, param_defs):
        self._sh = sh
        self._name = name
        self._return_dtype_factory = return_type
        self._param_defs = param_defs
        
        # Create parameter instances from dtype factories
        self._parameters = {}
        for param_name, param_def in param_defs.items():
            param_instance = param_def.dtype_factory()
            # Bind the parameter instance to its name and generator
            param_instance._bind(sh, param_name, allow_init=False)
            self._parameters[param_name] = param_instance
        
        # Push contexts for function declaration and body
        self._sh._push_context(self)  # Function parameters are accessible here
        
        body = base.Scope()
        self._sh._push_context(body)  # Function body with local variables
        
    def __getattr__(self, name):
        '''Access parameter instances by name.'''
        try:
            return self._parameters[name]
        except KeyError as key_error:
            raise AttributeError(f"No parameter named '{name}'") from key_error
    
    def return_(self, value=None):
        '''Emit a return statement.'''
        if self._return_dtype_factory is None:
            if value is not None:
                raise RuntimeError('Return value type mismatch')
        else:
            dtype_class = self._return_dtype_factory._get_dtype()
            if not isinstance(value, dtype_class):
                raise RuntimeError('Return value type mismatch')

        self._sh._emit_indent()
        self._sh._emit(
            'return{};\n'.format(' ' + str(value) if value is not None else '')
        )

class Function:
    '''
    Callable representing a function. Holds metadata for reflection
    and function calls. Has independent lifetime from FunctionDecl.
    '''
    def __init__(self, sh, name, return_type, param_defs):
        self._sh = sh
        self._name = name
        self._return_dtype_factory = return_type
        # Make a copy of parameter definitions for reflection
        self._param_defs = dict(param_defs)

    def __call__(self, **kwargs):
        '''Generate a function call.'''
        arg_list = []

        for param_name, param_def in self._param_defs.items():
            arg = kwargs.get(param_name)
            if arg is None:
                raise RuntimeError(
                    f"Argument missing for parameter '{param_name}'"
                )
            # Get the dtype class from the factory and use it for type checking
            dtype_class = param_def.dtype_factory._get_dtype()
            ref = dtype_class._get_value_ref(arg)
            if ref is None:
                raise RuntimeError(
                    f"Parameter '{param_name}' type mismatch"
                )
            
            arg_list.append(str(ref))
            kwargs.pop(param_name)

        if kwargs:
            unmatched_arg_names = ', '.join([
                f"'{name}'" for name in kwargs.keys()
            ])

            raise RuntimeError(
                f'Arguments without matching parameters: {unmatched_arg_names}'
            )

        arg_str = ', '.join(arg_list)
        
        # Handle void functions - they don't return a value
        if self._return_dtype_factory is None:
            # Emit the function call statement directly
            self._sh._emit_line_directive()
            self._sh._emit_indent()
            self._sh._emit(f'{self._name}({arg_str});\n')
            return None
        else:
            dtype_class = self._return_dtype_factory._get_dtype()
            return self._sh._instantiate_dtype(
                dtype_class,
                f'{self._name}({arg_str})'
            )
    
class _ConditionalStatement:
    def __init__(self, sh):
        self._sh = sh

    @abc.abstractmethod
    def _emit_statement(self):
        pass

    def __enter__(self):
        self._sh._emit_line_directive()
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

    def _emit_statement(self):
        self._sh._emit(f'if ({self._condition})\n')

class Else(_ConditionalStatement):
    def _emit_statement(self):
        self._sh._emit('else\n')
