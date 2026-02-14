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


    def _generate_test_uniforms(self, sh):
        with sh.uniform_buffer(
            name='cb',
            dx_register=0,
            vk_set=0,
            vk_binding=0
        ):
            sh.uniform('g_f3A', sh.Float3)
            sh.uniform('g_f3B', sh.Float3)

    def _generate_ps_main_decl(self, sh, ctx, out_type=None):
        out_type = out_type or sh.Float4
        if isinstance(ctx, HlslTestContext):
            with sh.ps_output('PsOut') as PsOut:
                PsOut.SV_Target('color', out_type)
            return sh.entry_point(ctx._entry_point_name, sh.PsOut)()
        else:
            sh.out_f4Color = sh.stage_output(out_type, location = 0)
            return sh.entry_point(ctx._entry_point_name)()

    @ctx_cls_hg
    def test_struct_emit_false(self, ctx_cls):
        """Test that emit=False registers type without emitting code.
        
        Writes struct definition directly to file first, then acquires
        without emission, then uses it in a function.
        """
        ctx = ctx_cls(dummy_entry_point = False)
        with ctx as sh:
            self._generate_test_uniforms(sh)

            # Write struct definition directly (simulates external definition)
            sh // 'The struct defined in the target language'
            if isinstance(ctx, HlslTestContext):
                sh._emit('struct ExternStruct { float3 response; float3 throughput; };\n\n')
            else:
                sh._emit('struct ExternStruct { vec3 response; vec3 throughput; };\n\n')
            
            # Acquire the struct without emitting code
            sh.struct('ExternStruct', emit = False)(
                response = sh.Float3,
                throughput = sh.Float3
            )
            
            # Type should be registered
            assert hasattr(sh, 'ExternStruct')
            
            # Use the acquired struct in a function
            with sh.function('computeStruct', sh.ExternStruct)(
                a = sh.Float3, b = sh.Float3
            ):
                sh // 'Now, use the struct'
                sh.result = sh.ExternStruct()
                sh.result.response = sh.a
                sh.result.throughput = sh.b
                sh.return_(sh.result)

            # Use in main shader to force compilation
            with self._generate_ps_main_decl(sh, ctx, sh.Float4):
                sh.s = sh.computeStruct(a = sh.g_f3A, b = sh.g_f3B)
                # Output flattened result
                sh.final_color = sh.Float4(
                    xyz = sh.s.response + sh.s.throughput, 
                    w = 1.0
                )
                
                if isinstance(ctx, HlslTestContext):
                    sh.out_struct = sh.PsOut()
                    sh.out_struct.color = sh.final_color
                    sh.return_(sh.out_struct)
                else:
                    sh.out_f4Color = sh.final_color

    @ctx_cls_hg
    def test_struct_emit_false_in_function(self, ctx_cls):
        """Test that acquired struct can be used as function return type."""
        ctx = ctx_cls(dummy_entry_point = False)
        with ctx as sh:
            self._generate_test_uniforms(sh)

            # Write struct definition directly
            sh // 'The struct defined in the target language'
            if isinstance(ctx, HlslTestContext):
                sh._emit('struct BSDF { float3 response; float3 throughput; };\n\n')
            else:
                sh._emit('struct BSDF { vec3 response; vec3 throughput; };\n\n')
            
            # Acquire struct without emission
            sh.struct('BSDF', emit = False)(
                response = sh.Float3,
                throughput = sh.Float3
            )
            
            # Define a function that returns the struct using Metashade
            # This verifies the struct type works in function signatures and bodies
            with sh.function('getBsdf', sh.BSDF)(
                r = sh.Float3, t = sh.Float3
            ):
                sh // 'Now, use the struct'
                sh.b = sh.BSDF()
                sh.b.response = sh.r
                sh.b.throughput = sh.t
                sh.return_(sh.b)

            # Use in main shader
            with self._generate_ps_main_decl(sh, ctx, sh.Float4):
                sh.bsdf = sh.getBsdf(r = sh.g_f3A, t = sh.g_f3B)
                
                sh.final = sh.Float4(
                    xyz = sh.bsdf.response * sh.bsdf.throughput,
                    w = 1.0
                )

                if isinstance(ctx, HlslTestContext):
                    sh.out_struct = sh.PsOut()
                    sh.out_struct.color = sh.final
                    sh.return_(sh.out_struct)
                else:
                    sh.out_f4Color = sh.final
