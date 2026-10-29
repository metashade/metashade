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

import os, shutil, subprocess, tempfile
from pathlib import Path
from metashade.util import perf

def find_executable() -> str:
    '''
    Find ``oslc`` on ``PATH``, falling back to ``$OSL_ROOT/bin``.
    '''
    oslc = shutil.which('oslc')
    if oslc is None:
        osl_root = os.environ.get('OSL_ROOT')
        if osl_root:
            oslc = shutil.which('oslc', path = str(Path(osl_root) / 'bin'))
    if oslc is None:
        raise FileNotFoundError('oslc not found on PATH or in $OSL_ROOT/bin')
    return oslc

def compile(
    src_path : str,
    output_path : str = None,
    include_paths = None
):
    args = [find_executable(), '-Werror']

    if include_paths:
        for path in include_paths:
            args.append(f'-I{path}')

    # oslc can't write to os.devnull on Windows, so without an output path
    # the .oso goes to a temporary directory.
    with tempfile.TemporaryDirectory() as tmp_dir:
        if output_path is None:
            output_path = Path(tmp_dir) / f'{Path(src_path).stem}.oso'

        args += ['-o', str(output_path), str(src_path)]

        with perf.TimedScope(f'oslc compiling to {output_path}'):
            result = subprocess.run(args)

    result.check_returncode()
