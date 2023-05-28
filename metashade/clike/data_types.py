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
import numbers

class BaseType(base.BaseType):
    @classmethod
    def _define_static(
        cls, sh, identifier,
        semantic = None, initializer = None, annotations = None
    ):
        sh._emit(
            '{type_name} {identifier}{semantic}'.format(
                type_name = cls._get_target_type_name(),
                identifier = identifier,
                semantic = '' if semantic is None \
                    else f' : {semantic}'
            )
        )

        if annotations is not None and annotations:
            sh._emit(' <\n')
            sh._push_indent()
            for annotation in annotations:
                sh._emit_indent()
                sh._emit(f'{annotation};\n')
            sh._pop_indent()
            sh._emit_indent()
            sh._emit('>')

        if initializer is not None:
            sh._emit(f' = {initializer}')

    def _define(
        self, sh, identifier,
        semantic = None, allow_init = True, annotations = None
    ):
        self._bind(sh, identifier, allow_init)
        self.__class__._define_static(
            sh, self._name, initializer = self._expression,
            semantic = semantic, annotations = annotations
        )

    def _assign(self, value):
        value_ref = self.__class__._get_value_ref(value)
        if value_ref is None:
            raise ArithmeticError('Type mismatch')

        self._expression = value
        self._sh._emit_indent()
        self._sh._emit( f'{self._name} = {value_ref};\n' )

    def __setattr__(self, name, value):
        if name == '_':
            self._assign(value)
        else:
            object.__setattr__(self, name, value)

    @classmethod
    def _get_target_type_name(cls):
        try:
            return cls._target_name
        except AttributeError:
            return cls.__name__

class ArithmeticType(BaseType):
    @staticmethod
    def _format_binary_operator(lhs : str, rhs : str, op : str) -> str:
        return f'({lhs} {op} {rhs})'

    def _rhs_binary_operator(self, rhs, op):
        rhs_ref = self.__class__._get_value_ref(rhs)
        if rhs_ref is None:
            return NotImplemented

        return self._sh._instantiate_dtype(
            self.__class__,
            self.__class__._format_binary_operator(
                lhs = self,
                rhs = rhs_ref,
                op = op
            )
        )

    def __add__(self, rhs):
        return self._rhs_binary_operator(rhs, '+')

    def __sub__(self, rhs):
        return self._rhs_binary_operator(rhs, '-')

    def __mul__(self, rhs):
        return self._rhs_binary_operator(rhs, '*')

    def __div__(self, rhs):
        return self._rhs_binary_operator(rhs, '/')
    
    def __truediv__(self, rhs):
        return self._rhs_binary_operator(rhs, '/')
    
    def __neg__(self):
        return self.__class__(f'-{self}')

class Float(ArithmeticType):
    _target_name = 'float'

    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        return (str(value) if isinstance(value, numbers.Number)
            else super()._get_value_ref_static(concrete_cls, value)
        )