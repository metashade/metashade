# Copyright 2024 Pavlo Penenko
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


class GlslNoVersionTestContext(_base.GlslTestContext):
    """GLSL test context that generates shaders without a version directive.
    
    The version is provided to glslang on the command line instead of in the shader.
    """
    
    def _create_generator(self):
        return _base.frag.Generator(self._file, glsl_version="")
    
    def _compile(self):
        _base.glslang.compile(
            src_path=self._src_path,
            target_env='vulkan1.1',
            shader_stage='frag',
            output_path=_base.os.devnull,
            glsl_version='450'
        )


class TestGlslVersion:
    def test_glsl_no_version(self):
        """Test that GLSL generator can omit the #version directive."""
        with GlslNoVersionTestContext() as sh:
            sh.out_f4Color = sh.stage_output(sh.Float4, location=0)

            with sh.entry_point('main')():
                sh.out_f4Color = sh.Float4((1.0, 0.0, 0.0, 1.0))
