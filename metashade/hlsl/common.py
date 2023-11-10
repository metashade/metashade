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

import pathlib, subprocess
import metashade.util as util

def identify_dxc():
    print('Found DXC executables (using the top one):')
    args = [
        'where',
        'dxc'
    ]

    dxc_result = subprocess.run( args, capture_output = True )
    print( dxc_result.stdout.decode() )
    
    args = [
        'dxc',
        '--version'
    ]

    dxc_result = subprocess.run( args, capture_output = True )
    print( dxc_result.stdout.decode() )

def compile(
    src_path : str,
    entry_point_name : str,
    profile : str,
    include_paths = None,
    to_spirv : bool = False,
    output_to_file : bool = False
) -> int:
    args = [
        'dxc',
        '-T', profile,
        '-E', entry_point_name,
        src_path
    ]

    if to_spirv:
        args.append('-spirv')

    if include_paths:
        for path in include_paths:
            args += ['-I', path]

    message = 'Compiling'
    if output_to_file:
        out_path = pathlib.Path(src_path).with_suffix(
            '.spv' if to_spirv else '.cso'
        )
        args += ['-Fo', out_path]
        message += f' {out_path}'

    with util.TimedScope(message):
        dxc_result = subprocess.run( args, capture_output = True )

    if dxc_result.returncode != 0:
        print( f'DXC compilation failed with code {dxc_result.returncode}, '
            f'stderr:\n{dxc_result.stderr.decode()}'
        )
    return dxc_result.returncode
