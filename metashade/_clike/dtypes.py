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

import metashade._base.dtypes as base
import numbers
from enum import Enum, auto

class ExprType(Enum):
    """Expression type for determining when parentheses are needed."""
    NONE = auto()       # Simple term (variable, literal) - no wrapping
    ARITHMETIC = auto() # Compound expression (a + b) - wrap in binary ops
    NEGATION = auto()   # Negation result (-a) - wrap only when negating again

class BaseType(base.BaseType):
    @classmethod
    def _format_uniform_register(cls, register_idx : int) -> str:
        raise RuntimeError('Uniform registers not supported for {cls}')
    
    @staticmethod
    def _emit_semantic(sh, semantic):
        if semantic is not None:
            sh._emit(f' : {semantic}')

    @classmethod
    def _emit_register(cls, sh, register):
        if register is not None:
            sh._emit(f' : register({cls._format_uniform_register(register)})')

    @classmethod
    def _emit_qualifiers(cls, sh, qualifiers):
        """Helper method to emit parameter qualifiers"""
        if qualifiers:
            for qualifier in qualifiers:
                qualifier_str = qualifier.direction.value
                if qualifier_str:
                    sh._emit(f'{qualifier_str} ')

    @classmethod
    def _emit_def(
        cls, sh, identifier,
        semantic = None,
        register : int = None,
        initializer = None,
        qualifiers = None
    ):
        '''
        https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-variable-syntax
        '''
        cls._emit_qualifiers(sh, qualifiers)
        
        sh._emit(
            '{type_name} {identifier}'.format(
                type_name = cls._get_target_type_name(),
                identifier = identifier
            )
        )

        cls._emit_semantic(sh, semantic)
        cls._emit_register(sh, register)

        if initializer is not None:
            sh._emit(f' = {initializer}')

    def _define(
        self, sh, identifier,
        allow_init = True,
        semantic = None,
        register = None,
        qualifiers = None
    ):
        self._bind(sh, identifier, allow_init)
        self.__class__._emit_def(
            sh, self._name,
            initializer = self._expression,
            semantic = semantic,
            register = register,
            qualifiers = qualifiers
        )

    def _assign(self, value):
        if value is self:
            return

        if isinstance(value, BaseType) and str(self) == str(value):
            return

        value_ref = self.__class__._get_value_ref(value)
        if value_ref is None:
            raise ArithmeticError('Type mismatch')

        self._sh._emit_indent()
        self._sh._emit( f'{self} = {value_ref};\n' )

    def _assign_op(self, value, op):
        value_ref = self.__class__._get_value_ref(value)
        if value_ref is None:
            raise ArithmeticError('Type mismatch')

        self._sh._emit_indent()
        self._sh._emit( f'{self} {op}= {value_ref};\n' )

    @classmethod
    def _get_target_type_name(cls):
        return cls._target_name

class ArithmeticType(BaseType):
    def __init__(self, _=None):
        super().__init__(_)
        self._expr_type = ExprType.NONE

    def _bind(self, sh, name, allow_init):
        super()._bind(sh, name, allow_init)
        self._expr_type = ExprType.NONE

    @staticmethod
    def _needs_parens_in_binary_op(operand) -> bool:
        """Check if operand needs parentheses in a binary operation."""
        expr_type = getattr(operand, '_expr_type', ExprType.NONE)
        return expr_type == ExprType.ARITHMETIC

    @staticmethod
    def _format_binary_operator(lhs : str, rhs : str, op : str) -> str:
        lhs_expr = str(lhs)
        if ArithmeticType._needs_parens_in_binary_op(lhs):
            lhs_expr = f'({lhs_expr})'

        rhs_expr = str(rhs)
        if ArithmeticType._needs_parens_in_binary_op(rhs):
            rhs_expr = f'({rhs_expr})'

        return f'{lhs_expr} {op} {rhs_expr}'

    def _rhs_binary_operator(self, rhs, op):
        rhs_ref = self.__class__._get_value_ref(rhs)
        if rhs_ref is None:
            return NotImplemented

        result = self._sh._instantiate_dtype(
            self.__class__,
            self.__class__._format_binary_operator(
                lhs = self,
                rhs = rhs_ref,
                op = op
            )
        )
        result._expr_type = ExprType.ARITHMETIC
        return result

    def _inplace_binary_operator(self, rhs, op):
        if not self._is_lvalue:
             raise RuntimeError("Can't modify an rvalue")
        self._assign_op(rhs, op)
        return self

    def __add__(self, rhs):
        return self._rhs_binary_operator(rhs, '+')

    def __iadd__(self, rhs):
        return self._inplace_binary_operator(rhs, '+')

    def __sub__(self, rhs):
        return self._rhs_binary_operator(rhs, '-')

    def __isub__(self, rhs):
        return self._inplace_binary_operator(rhs, '-')

    def __mul__(self, rhs):
        return self._rhs_binary_operator(rhs, '*')

    def __imul__(self, rhs):
        return self._inplace_binary_operator(rhs, '*')

    def __div__(self, rhs):
        return self._rhs_binary_operator(rhs, '/')
    
    def __truediv__(self, rhs):
        return self._rhs_binary_operator(rhs, '/')

    def __itruediv__(self, rhs):
        return self._inplace_binary_operator(rhs, '/')
    
    def __neg__(self):
        val_str = str(self)
        expr_type = getattr(self, '_expr_type', ExprType.NONE)
        # Wrap if arithmetic expression OR if already a negation (avoid --a)
        if expr_type in (ExprType.ARITHMETIC, ExprType.NEGATION):
            val_str = f'({val_str})'
        result = self._sh._instantiate_dtype(self.__class__, f'-{val_str}')
        result._expr_type = ExprType.NEGATION
        return result

class Scalar(ArithmeticType):
    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        return (str(value) if isinstance(value, numbers.Number)
            else super()._get_value_ref_static(concrete_cls, value)
        )

class Float(Scalar):
    _target_name = 'float'

class Int(Scalar):
    _target_name = 'int'

