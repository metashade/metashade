# Copyright 2026 Pavlo Penenko
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

"""
Tests for struct definition and acquisition.
"""

from __future__ import annotations

import pytest
from metashade.util.testing import ctx_cls_hg, HlslTestContext


class TestStructDefinition:
    """Tests for defining structs with sh.struct()."""

    @ctx_cls_hg
    def test_struct_emission(self, ctx_cls):
        """Test that sh.struct() emits correct code and compiles."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            sh.struct('TestStruct')(
                a=sh.Float,
                b=sh.Float3,
                c=sh.Float2
            )

    @ctx_cls_hg
    def test_struct_registration(self, ctx_cls):
        """Test that struct type is registered on generator."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            sh.struct('MyStruct')(x=sh.Float, y=sh.Float)
            
            # Struct type should be accessible
            assert hasattr(sh, 'MyStruct')

    @ctx_cls_hg
    def test_struct_emit_false(self, ctx_cls):
        """Test that emit=False registers type without emitting code.
        
        Writes struct definition directly to file first, then acquires
        without emission, then uses it in a function.
        """
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            # Write struct definition directly (simulates external definition)
            if isinstance(ctx, HlslTestContext):
                sh._emit('struct ExternStruct { float3 response; float3 throughput; };\n\n')
            else:
                sh._emit('struct ExternStruct { vec3 response; vec3 throughput; };\n\n')
            
            # Acquire the struct without emitting code
            sh.struct('ExternStruct', emit=False)(
                response=sh.Float3,
                throughput=sh.Float3
            )
            
            # Type should be registered
            assert hasattr(sh, 'ExternStruct')
            
            # Use the acquired struct in a function
            with sh.function('useStruct')(s=sh.ExternStruct):
                sh.result = sh.s.response + sh.s.throughput
                sh.return_()

    @ctx_cls_hg
    def test_struct_emit_false_in_function(self, ctx_cls):
        """Test that acquired struct can be used as function return type."""
        ctx = ctx_cls(dummy_entry_point=True)
        with ctx as sh:
            # Write struct definition directly
            if isinstance(ctx, HlslTestContext):
                sh._emit('struct BSDF { float3 response; float3 throughput; };\n\n')
            else:
                sh._emit('struct BSDF { vec3 response; vec3 throughput; };\n\n')
            
            # Acquire struct without emission
            sh.struct('BSDF', emit=False)(
                response=sh.Float3,
                throughput=sh.Float3
            )
            
            # Declare a function that returns the struct
            sh.function('getBsdf', sh.BSDF)().declare()
