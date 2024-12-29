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
import _base
from metashade.hlsl.sm6 import ps_6_0

class TestUniforms(_base.TestBase):
    def test_cb_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with sh.uniform_buffer(register = 0, name = 'cb0'):
                sh.uniform('g_f0', sh.Float4)

            with sh.uniform_buffer(register = 1, name = 'cb1'):
                sh.uniform('g_f1', sh.Float4)

            with pytest.raises(Exception):
                with sh.uniform_buffer(register = 0, name = 'cb2'):
                    sh.uniform('g_f2', sh.Float4)

    def test_cb_string_register(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(register = 'blahblah', name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_cb_negative_register(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(register = -1, name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_simple_cb(self):
        with _base.GlslTestContext() as sh:
            with sh.uniform_buffer(name = 'cb0', set = 0, binding = 0):
                sh.uniform('g_f4Color', sh.Float4)

            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)
            
            with sh.entry_point('main')():
                sh.out_f4Color = sh.g_f4Color

    def test_glsl_cb_string_set(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(set = 'blahblah', name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_string_location(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(location = 'blahblah', name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_negative_set(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(set = -1, name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_negative_location(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(Exception):
                with sh.uniform_buffer(location = -2, name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_texture_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            sh.uniform('g_t0', sh.Texture2d, register = 0)
            sh.uniform('g_t1', sh.Texture2d, register = 1)

            with pytest.raises(Exception):
                sh.uniform('g_t2', sh.Texture2d, register = 0)

    def test_sampler_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            sh.uniform('g_s0', sh.Sampler, register = 0)
            sh.uniform('g_s1', sh.Sampler, register = 1)
            
            with pytest.raises(Exception):
                sh.uniform('g_s2', sh.Sampler, register = 0)
