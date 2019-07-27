# Copyright 2019 Pavlo Penenko
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
This is as a rudimentary implementation of an HLSL FX file format generator.
It's not expected to be feature-complete.
While this format looks like a dead end as of 2019, it provides a minimalist
and self-contained way to test multiple shader stages working together in some
hosts, like FX Composer or Maya plugins.
"""

def simple_vs_ps_technique(target, vs_main_name, ps_main_name):
    template = """
RasterizerState DisableCulling
{{
    CullMode = NONE;
}};

DepthStencilState EnableDepth
{{
    DepthEnable = TRUE;
}};

BlendState DisableBlend
{{
    BlendEnable[0] = FALSE;
}};

technique10 Simple
{{
    pass Pass0
    {{
        SetVertexShader( CompileShader( vs_4_0, {vs_main_name}() ) );
        SetGeometryShader( NULL );
        SetPixelShader( CompileShader( ps_4_0, {ps_main_name}() ) );
        
        SetRasterizerState(DisableCulling);       
        SetDepthStencilState(EnableDepth, 0);
        SetBlendState(DisableBlend, float4( 0.0f, 0.0f, 0.0f, 0.0f ), 0xFFFFFFFF);
    }}
}}
"""
    target._write(template.format(vs_main_name=vs_main_name,
                                 ps_main_name=ps_main_name))