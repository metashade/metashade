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

class BaseType:
    _sh = None

    @classmethod
    def _set_generator(cls, sh)
        

    """
    The base class for all Metashade data types. Can represent either an
    lvalue or an rvalue.
    """    
    def __init__(self, expression : str = None):
        """
        Constructor. _name is always None at this point because it
        can only be assigned by the generator later by calling _bind()
        The value can be optionally initialized.
        """
        self._name = None
        self._expression = expression
        
    def _bind(self, sh, name, allow_init):
        if not allow_init and self._expression is not None:
            raise RuntimeError('Initializers are not supported.')
        
        self._name = name
        self._sh = sh
        
    def __str__(self) -> str:
        if self._name is not None:
            return self._name
        elif self._expression is not None:
            return self._expression
        else:
            raise RuntimeError(
                'Instance is neither a variable nor an expression.'
            )

    @classmethod
    def _get_value_ref(cls, value):
        return cls._get_value_ref_static(cls, value)

    @staticmethod
    def _get_value_ref_static(concrete_cls, value):
        return value if isinstance(value, concrete_cls) else None
