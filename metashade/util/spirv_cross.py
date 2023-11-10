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

import pathlib, shutil, subprocess
from metashade.util import perf

_exe_name = 'spirv-cross'

def identify():
    print(f'Found SPIRV-Cross executable: {shutil.which(_exe_name)}')

def spirv_to_glsl(spirv_path : str):
    glsl_path = pathlib.Path(spirv_path).with_suffix('.glsl')
    args = [
        _exe_name,
        '--output', glsl_path,
        spirv_path
    ]

    with perf.TimedScope(f'SPIRV-Cross generating {glsl_path}'):
        result = subprocess.run( args, capture_output = True )
