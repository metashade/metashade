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

class Scope:
    """
    Represents a scope in a C-like language storing a dictionary of its local
    symbols.
    """
    def __init__(self):
        self._locals = dict()
        
    def __getattr__(self, name):
        try:
            return self._locals[name]
        except KeyError as key_error:
            raise AttributeError(
                f"No local symbol named '{name}'"
            ) from key_error
