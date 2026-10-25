# Copyright 2023 Pavlo Penenko
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

import pytest
from metashade.util.testing import ctx_cls_hg

class TestDTypes:
    @ctx_cls_hg
    def test_init_from_literal(self, ctx_cls):
        with ctx_cls(dummy_entry_point = True) as sh:
            with sh.function('test', sh.Float)():
                sh.f4A = sh.Float4(1.0)
                sh.f4B = sh.Float4(0.0) - sh.f4A
                
                sh.f3A = sh.Float3(0.0)
                sh.f3B = sh.f3A + sh.Float3(1.0)

                sh.f2A = sh.Float2(0.6578467)
                sh.f2B = sh.Float2(0.4235) * sh.f2A

                sh.fA = sh.Float(1.0)
                sh.fB = sh.Float(2.0) + sh.fA

                sh.return_(sh.f4B.w + sh.f3B.z + sh.f2B.y + sh.fB)


    # Initializers that have no valid value reference for the target dtype.
    # Before the fix, these were silently stringified to the expression
    # 'None' (or, for Int(1.5), to a float literal in an int initializer).
    _invalid_initializers = [
        ('Int', lambda sh: True, 'bool'),
        ('Int', lambda sh: 1.5, 'float'),
        ('Bool', lambda sh: 1, 'int'),
        ('Float', lambda sh: sh.Int(1), 'Int'),
        ('Float', lambda sh: object(), 'object'),
        ('Float', lambda sh: [1.0], 'list'),
        ('Float3', lambda sh: sh.Int(1), 'Int'),
        ('Float4', lambda sh: True, 'bool'),
        ('Float4', lambda sh: sh.Float3(1.0), 'Float3'),
    ]

    @ctx_cls_hg
    @pytest.mark.parametrize(
        'dtype_name, make_value, value_type_name',
        _invalid_initializers,
        ids = [
            f'{dtype}-{value_type}'
            for dtype, _, value_type in _invalid_initializers
        ]
    )
    def test_init_type_mismatch(
        self, ctx_cls, dtype_name, make_value, value_type_name
    ):
        with ctx_cls(no_file = True) as sh:
            dtype_factory = getattr(sh, dtype_name)
            value = make_value(sh)
            with pytest.raises(
                TypeError,
                match = (
                    f"Cannot initialize '{dtype_name}' "
                    f"from '{value_type_name}'"
                )
            ):
                dtype_factory(value)

    @ctx_cls_hg
    def test_init_type_mismatch_in_local(self, ctx_cls):
        """A mismatched initializer must not emit 'float f = None;'."""
        with ctx_cls(no_file = True) as sh:
            with sh.function('test', sh.Float)(i = sh.Int):
                with pytest.raises(
                    TypeError,
                    match = "Cannot initialize 'Float' from 'Int'"
                ):
                    sh.f = sh.Float(sh.i)
