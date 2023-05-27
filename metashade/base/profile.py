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

from . import data_types
from . import context

import copy, inspect, sys

class Generator:
    """
    The base class for generators. Wraps an output file.
    """
    def __init__(self, file_):
        self._file = file_
        
        self._indent = 0
        self._indent_char = '\t'
        self._indent_delta = 1
        
        self._globals = dict()
        self._context_stack = list()

    class _DtypeFactory:
        def __init__(self, sh, dtype):
            self._sh = sh
            self._dtype = dtype

        def _get_dtype(self):
            return self._dtype

        def __call__(self, *args, **kwargs):
            value = self._dtype(*args, **kwargs)
            value._set_generator(self._sh)
            return value

    def _register_dtypes(self, dtype_module_name : str):
        for dtype_name, dtype in inspect.getmembers(
            sys.modules[dtype_module_name],
            lambda member: (inspect.isclass(member)
                and member.__module__ == dtype_module_name
                and not member.__name__.startswith('_')
        )):
            setattr(self, dtype_name, self._DtypeFactory(self, dtype))
        
    def _push_indent(self):
        self._indent += self._indent_delta
        
    def _pop_indent(self):
        self._indent -= self._indent_delta
        
    def _emit_indent(self):
        return self._file.write(
            self._indent_char * (self._indent * self._indent_delta))
    
    def _emit(self, line):
        self._file.write(line)
        
    def _push_context(self, context):
        self._context_stack.append(context)
        
    def _pop_context(self):
        self._context_stack.pop()

    def _check_unique_attr(self, name):
        exists = False
        try:
            getattr(self, name)
            exists = True
        except AttributeError:
            pass
        
        if exists:
            raise AttributeError(
                f"'{name}': can't redefine Metashade symbol already "
                "defined in the context stack"
            )

    @staticmethod
    def _check_public_name(name : str):
        if name.startswith('_'):
            raise RuntimeError(
                f"'{name}': symbols starting with an underscore"
                "are reserved for Metashade implementation"
            )

    def _check_global_scope(self):
        return len(self._context_stack) == 0

    def _set_global(self, name, value):
        self._check_unique_attr(name)
        self._globals[name] = value

    def __getattr__(self, name):
        for context in reversed(self._context_stack):
            try:
                return getattr(context, name)
            except AttributeError:
                pass
        try:
            return self._globals[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        if ( name.startswith('_')
            or isinstance(value, self._DtypeFactory)
        ):
            object.__setattr__(self, name, value)
            return

        lvalue = getattr(self, name, None)
        if isinstance(lvalue, data_types.BaseType):
            # An lvalue with the given name exists,
            # so assign the new value to it
            lvalue._assign(value)
            return

        # If value is an lvalue, we need to clone it
        if (isinstance(value, data_types.BaseType)
            and value._name is not None
        ):
            value = copy.copy(value)
            value._expression = value._name

        # Define a new local
        self._context_stack[-1]._locals[name] = value
        self._emit_indent()
        value._define(self, name)
        self._emit(';\n')
