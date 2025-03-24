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

from metashade.modules import export

@export
def py_add(sh, a : 'Float4', b : 'Float4') -> 'Float4':
    sh.c = a + b
    sh.return_(sh.c)

@export
def py_mul(sh, a : 'Float4', b : 'Float4') -> 'Float4':
    sh.c = a * b
    sh.return_(sh.c)

@export
def py_madd(sh, a : 'Float4', b : 'Float4', c : 'Float4') -> 'Float4':
    sh.d = sh.py_add(a = a, b = b)
    sh.e = sh.py_mul(a = sh.d, b = c)
    sh.return_(sh.e)
