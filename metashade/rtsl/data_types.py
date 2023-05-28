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

import collections, numbers, sys
import metashade.clike.data_types as clike
from metashade.clike.data_types import Float

def _check_float_type(dtype):
    if not issubclass(dtype, Float):
        raise RuntimeError(
            'Vectors of types other than 32-bit float are not implemented yet'
        )

class _RawVector(clike.ArithmeticType):
    _swizzle_str = 'xyzw'

    @classmethod
    def _get_related_type_name(cls, dim : int):
        _check_float_type(cls._element_type)
        return f'Float{dim}'

    @classmethod
    def _get_related_type(cls, dim : int):
        if dim == 1:
            return cls._element_type

        if dim not in range(2, 5):
            raise RuntimeError('Unsupported vector width')

        type_name = cls._get_related_type_name(dim)
        return getattr(sys.modules[cls.__module__], type_name)

    def __getattr__(self, name):
        is_valid_swizzle = False
        try:
            is_valid_swizzle = len(name) <= 4 and all(
                self.__class__._swizzle_str.index(ch) < self.__class__._dim
                    for ch in name
            )
        except ValueError:
            pass

        if is_valid_swizzle:
            dtype = self._get_related_type(len(name))
            return self._sh._instantiate_dtype(
                dtype,
                '.'.join((str(self), name))
            )
        else:
            raise AttributeError

    def _check_dims(self, rhs):
        if rhs.__class__._dim != self.__class__._dim:
            raise ArithmeticError(
                'Operands must have the same dimensions.'
            )

    def _check_mul(self, matrix):
        if matrix.__class__._dims[0] != self.__class__._dim:
            raise ArithmeticError(
                'The number of rows in the matrix must be equal to the size of'
                ' the vector'
            )

    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        parent_result = super()._get_value_ref_static(concrete_cls, value)
        if parent_result is not None:
            return parent_result

        if (isinstance(value, collections.Sequence)
            and not isinstance(value, str)
            and len(value) == concrete_cls._dim
            and all( isinstance(element, numbers.Number)
                or isinstance(element, concrete_cls._element_type)
                    for element in value
            )
        ):
            return concrete_cls(', '.join(map(str, value)))
        else:
            return None
        
    @classmethod
    def _get_binary_operator_result_type(cls):
        return cls

    def _rhs_binary_operator(self, rhs, op : str):
        if self.__class__ != rhs.__class__:
            return NotImplemented

        self._check_dims(rhs)

        return_type = self.__class__._get_binary_operator_result_type()
        return return_type(
            self.__class__._format_binary_operator(
                self, rhs, op
            )
        )

    @classmethod
    def _scalar_mul(cls, lhs : str, rhs : str):
        return cls(cls._format_binary_operator(lhs, rhs, '*'))

    def __mul__(self, rhs):
        per_element_result = self._rhs_binary_operator(rhs, '*')
        if per_element_result != NotImplemented:
            return per_element_result

        if rhs.__class__ == self._element_type:
            return self.__class__._scalar_mul(self, rhs)
        else:
            return NotImplemented

    def __rmul__(self, lhs):
        lhs_ref = self._element_type._get_value_ref(lhs)
        if lhs_ref is not None:
            return self.__class__._scalar_mul(lhs_ref, self)
        else:
            return NotImplemented

    def dot(self, rhs):
        self._check_dims(rhs)
        return self._sh._instantiate_dtype(
            self.__class__._element_type,
            f'dot({self}, {rhs})'
        )

class Float1(_RawVector):
    _dim = 1

class Float2(_RawVector):
    _dim = 2

class Float3(_RawVector):
    _dim = 3

    def cross(self, rhs):
        if rhs.__class__ != self.__class__:
            raise ArithmeticError(
                'Cross product operands must have the same type (3D vector)'
            )
        return self._sh._instantiate_dtype(
            self.__class__, f'cross({self}, {rhs})'
        )

class Float4(_RawVector):
    _dim = 4

class _RawMatrix(clike.ArithmeticType):
    @classmethod
    def _get_related_type_name(cls, dims):
        _check_float_type(cls._element_type)
        return 'Float{rows}x{cols}'.format(rows = dims[0], cols = dims[1])

    @classmethod
    def _get_related_type(cls, dims):
        if dims[0] == 1 and dims[1] == 1:
            return cls._element_type

        if any(dim not in range(1, 5) for dim in dims):
            raise RuntimeError('Unsupported matrix width')

        type_name = cls._get_related_type_name(dims)
        return getattr(sys.modules[cls.__module__], type_name)

    def _check_mul(self, vector):
        dim_idx = 1 if self._sh._matrix_post_multiplication else 0
        if self.__class__._dims[dim_idx] != vector.__class__._dim:
            raise ArithmeticError(
                'The number of columns in the matrix must be equal to the size'
                'of the vector'
            )

    def transpose(self):
        result_type = self._get_related_type(
            (self.__class__._dims[1], self.__class__._dims[0])
        )
        return self._sh._instantiate_dtype( result_type, f'transpose({self})' )

# Generate all concrete matrix types to avoid copy-and-paste
for rows in range(1, 5):
    for cols in range(1, 5):
        name = f'Float{rows}x{cols}'
        globals()[name] = type(
            name,
            (_RawMatrix,),
            {'_dims' : (rows, cols)}
        )

class _Matrix(_RawMatrix):
    @classmethod
    def _get_related_type_name(cls, dims):
        _check_float_type(cls._element_type)
        return 'Matrix{rows}x{cols}f'.format(rows = dims[0], cols = dims[1])

def _get_vector_type_name(element_type, dim : int):
    _check_float_type(element_type)
    return f'Vector{dim}f'

class _Vector(_RawVector):
    @classmethod
    def _get_related_type_name(cls, dim : int):
        return _get_vector_type_name(cls._element_type, dim)

class Vector2(_Vector):
    _dim = 2

class Vector3(_Vector):
    _dim = 3

    def as_vector4(self):
        vector4_type = self.__class__._get_related_type(4)
        return self._sh._instantiate_dtype(vector4_type, xyz = self, w = 0.0)

class Vector4(_Vector):
    _dim = 4
    def as_vector4(self):
        return self

class _Point(_RawVector):
    @classmethod
    def _get_related_type_name(cls, dim : int):
        _check_float_type(cls._element_type)
        return f'Point{dim}f'
    
    @classmethod
    def _get_binary_operator_result_type(cls):
        vector_type = getattr(
            sys.modules[cls.__module__],
            _get_vector_type_name(cls._element_type, cls._dim)
        )
        return vector_type

class Point2(_Point):
    _dim = 2

class Point3(_Point):
    _dim = 3

    def as_vector4(self):
        vector4_type = getattr(
            sys.modules[self.__class__.__module__],
            _get_vector_type_name(self.__class__._element_type, 4)
        )
        return self._sh._instantiate_dtype(vector4_type, xyz = self, w = 1.0)

class RgbF:
    pass

class RgbaF:
    pass
