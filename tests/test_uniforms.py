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

class TestUniforms(_base.TestBase):
    def test_hlsl_cb_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with sh.uniform_buffer(dx_register = 0, name = 'cb0'):
                sh.uniform('g_f0', sh.Float4)

            with sh.uniform_buffer(dx_register = 1, name = 'cb1'):
                sh.uniform('g_f1', sh.Float4)

            with pytest.raises(
                RuntimeError,
                match = 'Uniform register b0 is already in use by cb0'
            ):
                with sh.uniform_buffer(dx_register = 0, name = 'cb2'):
                    sh.uniform('g_f2', sh.Float4)

    def test_hlsl_cb_string_register(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = 'blahblah is not a valid index'
            ):
                with sh.uniform_buffer(dx_register = 'blahblah', name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_cb_negative_register(self):
        with _base.HlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = '-1 is not a valid index'
            ):
                with sh.uniform_buffer(dx_register = -1, name = 'cb0'):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_multi_set_binding(self):
        with _base.GlslTestContext() as sh:
            with sh.uniform_buffer(name = 'cb0', vk_set = 0, vk_binding = 0):
                sh.uniform('g_f4Color', sh.Float4)

            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)
            
            with sh.entry_point('main')():
                sh.out_f4Color = sh.g_f4Color

    def test_glsl_cb_multi_set_binding(self):
        with _base.GlslTestContext() as sh:
            with sh.uniform_buffer(name = 'cb0', vk_set = 0, vk_binding = 0):
                sh.uniform('g_f4Color0', sh.Float4)

            with sh.uniform_buffer(name = 'cb1', vk_set = 0, vk_binding = 1):
                sh.uniform('g_f4Color1', sh.Float4)

            with sh.uniform_buffer(name = 'cb2', vk_set = 1, vk_binding = 0):
                sh.uniform('g_f4Color2', sh.Float4)

            with sh.uniform_buffer(name = 'cb3', vk_set = 1, vk_binding = 1):
                sh.uniform('g_f4Color3', sh.Float4)

            sh.out_f4Color = sh.stage_output(sh.Float4, location = 0)
            
            with sh.entry_point('main')():
                sh.out_f4Color = sh.g_f4Color0

    def test_glsl_cb_set_binding_clash(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with sh.uniform_buffer(name = 'cb0', vk_set = 0, vk_binding = 0):
                sh.uniform('g_f4Color0', sh.Float4)

            with sh.uniform_buffer(name = 'cb1', vk_set = 0, vk_binding = 1):
                sh.uniform('g_f4Color1', sh.Float4)

            with pytest.raises(
                RuntimeError,
                match = 'Vulkan uniform binding 0 in descriptor set 0 '
                        'is already in use by cb0'
            ):
                with sh.uniform_buffer(
                    name = 'cb2', vk_set = 0, vk_binding = 0
                ):
                    sh.uniform('g_f4Color2', sh.Float4)

    def test_glsl_cb_string_set(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = 'blahblah is not a valid index'
            ):
                with sh.uniform_buffer(
                    vk_set = 'blahblah', vk_binding = 0, name = 'cb0'
                ):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_string_binding(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = 'blahblah is not a valid index'
            ):
                with sh.uniform_buffer(
                    vk_set = 0, vk_binding = 'blahblah', name = 'cb0'
                ):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_negative_set(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = '-1 is not a valid index'
            ):
                with sh.uniform_buffer(
                    vk_set = -1, vk_binding = 0, name = 'cb0'
                ):
                    sh.uniform('g_f0', sh.Float4)

    def test_glsl_cb_negative_binding(self):
        with _base.GlslTestContext(no_file = True) as sh:
            with pytest.raises(
                RuntimeError,
                match = '-2 is not a valid index'
            ):
                with sh.uniform_buffer(
                    vk_set = 0, vk_binding = -2, name = 'cb0'
                ):
                    sh.uniform('g_f0', sh.Float4)

    def test_texture_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            sh.uniform('g_t0', sh.Texture2d, dx_register = 0)
            sh.uniform('g_t1', sh.Texture2d, dx_register = 1)

            with pytest.raises(
                RuntimeError,
                match = 'Uniform register t0 is already in use by g_t0'
            ):
                sh.uniform('g_t2', sh.Texture2d, dx_register = 0)

    def test_sampler_register_clash(self):
        with _base.HlslTestContext(no_file = True) as sh:
            sh.uniform('g_s0', sh.Sampler, dx_register = 0)
            sh.uniform('g_s1', sh.Sampler, dx_register = 1)

            with pytest.raises(
                RuntimeError,
                match = 'Uniform register s0 is already in use by g_s0'
            ):
                sh.uniform('g_s2', sh.Sampler, dx_register = 0)
