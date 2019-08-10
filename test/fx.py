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

"""
Just a sketch of generating an HLSL effect with a trivial VS/PS pair.
Currently fails.
"""

import sys

import metashade.hlsl.profile as profile
import metashade.hlsl.data_types as t
import metashade.hlsl.fx as fx

def test_simple():
    sh = profile.Generator(sys.stderr)
    
    sh.vertex_shader_input('VsIn')(position = t.Point3f)
    sh.vertex_shader_output('VsOut')()
    
    with sh.vertex_shader_main('VsMain', sh.VsOut)(i = sh.VsIn):
        sh.o = sh.VsOut()        
        sh.o.position._ = t.Vector4f((0, 0, 0, 1))
        sh.return_(sh.o)
    
    sh.pixel_shader_output('PsOut')(color = t.RGBA)
    
    with sh.pixel_shader_main('PsMain', sh.PsOut)():
        sh.o = sh.PsOut()
        sh.o.color._ = t.RGBA((1, 0, 1, 1))
        sh.return_(sh.o)
        
    fx.simple_vs_ps_technique(sh, 'VsMain', 'PsMain')
