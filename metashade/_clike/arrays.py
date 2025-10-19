# Copyright 2025 Pavlo Penenko
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

from metashade._clike.dtypes import BaseType

class ArrayBase(BaseType):
    _sh = None
    _element_type = None
    _dims = None

    def __getitem__(self, index):
        return self._sh._instantiate_dtype(
            self._element_type,
            f'{self}[{index}]'
        )

    def __setitem__(self, index, value):
        raise NotImplementedError('Setting array elements not implemented yet')
    
    @classmethod
    def _emit_def(
        cls, sh, identifier,
        semantic = None,
        register : int = None,
        initializer = None,
        qualifiers = None
    ):
        # Emit all qualifiers if present
        if qualifiers:
            for qualifier in qualifiers:
                qualifier_str = sh.format_parameter_qualifiers(qualifier)
                if qualifier_str:
                    sh._emit(f'{qualifier_str} ')
        
        sh._emit(
            '{element_type} {identifier}{dims}'.format(
                element_type = cls._element_type._get_target_type_name(),
                identifier = identifier,
                dims = ''.join(f'[{dim}]' for dim in cls._dims)
            )
        )

        cls._emit_semantic(sh, semantic)
        cls._emit_register(sh, register)

        if initializer is not None:
            raise NotImplementedError('Array initialization not supported yet')

def create_array(element_type, dims):
    class_name = f"Array_{element_type.__name__}_{dims}"
    array_class = type(
        class_name,
        (ArrayBase,),
        {
            "_element_type": element_type,
            "_dims": dims
        }
    )
    return array_class