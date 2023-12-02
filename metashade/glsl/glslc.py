# Copyright 2022 Pavlo Penenko
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
from typing import NamedTuple
from metashade.util import perf

def identify():
    print(f'Found glslc executable: {shutil.which("glslc")}')
    
    args = [
        'glslc',
        '--version'
    ]
    result = subprocess.run( args, capture_output = True )
    print( result.stdout.decode() )

class CompilationResult(NamedTuple):
    returncode : int
    out_path : pathlib.Path

def compile(
    src_path : str,
    entry_point_name : str,
    target_env : str,
    shader_stage : str,
    include_paths = None,
    to_spirv : bool = False,
    output_to_file : bool = False
) -> CompilationResult:
    args = [
        'glslc',
        '--target-env', target_env,
        '-fshader-stage', shader_stage,
        '-fentry-point', entry_point_name,
        src_path
    ]

    if include_paths:
        for path in include_paths:
            args += ['-I', path]

    message = 'glslc compiling'
    if output_to_file:
        out_path = pathlib.Path(src_path).with_suffix('.spv')
        args += ['-o', out_path]
        message += f' {out_path}'

    with perf.TimedScope(message):
        result = subprocess.run( args, capture_output = True )

    if result.returncode != 0:
        print( f'DXC compilation failed with code {result.returncode}, '
            f'stderr:\n{result.stderr.decode()}'
        )
    
    return CompilationResult(
        returncode = result.returncode,
        out_path = out_path if output_to_file else None
    )
