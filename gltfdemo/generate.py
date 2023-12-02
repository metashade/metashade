# Copyright 2020 Pavlo Penenko
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

import argparse, functools, io, os, pathlib, subprocess, sys
import multiprocessing as mp
from typing import List, NamedTuple
from pygltflib import GLTF2

from metashade.hlsl import dxc
from metashade.util import perf, spirv_cross
from metashade.glsl import glslc

import _impl

class _Shader:
    def __init__(self, file_path):
        self._file_path = file_path

    @staticmethod
    def _get_entry_point_name():
        return None
    
    @staticmethod
    def _get_hlsl_profile():
        return None
    
    @staticmethod
    def _get_glsl_stage():
        return None

    def compile(self, to_glsl : bool) -> str:
        log = io.StringIO()
        log, sys.stdout = sys.stdout, log

        try:
            dxc_output_path = pathlib.Path(self._file_path).with_suffix(
                '.hlsl.spv' if to_glsl else '.cso'
            )
            
            dxc.compile(
                src_path = self._file_path,
                entry_point_name = self._get_entry_point_name(),
                profile = self._get_hlsl_profile(),
                to_spirv = to_glsl,
                output_path = dxc_output_path
            )

            if to_glsl:
                glsl_path = pathlib.Path(self._file_path).with_suffix('.glsl')
                spirv_cross.spirv_to_glsl(
                    spirv_path = dxc_output_path,
                    glsl_path = glsl_path
                )
                spv_path = pathlib.Path(self._file_path).with_suffix('.spv')
                glslc.compile(
                    src_path = glsl_path,
                    target_env = 'vulkan1.1',
                    shader_stage = self._get_glsl_stage(),
                    entry_point_name = self._get_entry_point_name(),
                    output_path = spv_path
                )
        except subprocess.CalledProcessError as err:
            pass
            

        log, sys.stdout = sys.stdout, log
        return log.getvalue()

class _VertexShader(_Shader):
    @staticmethod
    def _get_entry_point_name():
        return _impl.vs_main
    
    @staticmethod
    def _get_hlsl_profile():
        return 'vs_6_0'
    
    @staticmethod
    def _get_glsl_stage():
        return 'vertex'

class _PixelShader(_Shader):
    @staticmethod
    def _get_entry_point_name():
        return _impl.ps_main
    
    @staticmethod
    def _get_profile():
        return 'ps_6_0'
    
    @staticmethod
    def _get_glsl_stage():
        return 'fragment'

class _AssetResult(NamedTuple):
    log : io.StringIO
    shaders : List[_Shader]

def _process_asset(
        gltf_file_path : str,
        out_dir : str,
        skip_codegen : bool = False
) -> _AssetResult:
    log = io.StringIO()
    log, sys.stdout = sys.stdout, log

    shaders = []

    with perf.TimedScope(f'Loading glTF asset {gltf_file_path} '):
        gltf_asset = GLTF2().load(gltf_file_path)

    for mesh_idx, mesh in enumerate(gltf_asset.meshes):
        mesh_name = ( mesh.name if mesh.name is not None
            else f'UnnamedMesh{mesh_idx}'
        )

        for primitive_idx, primitive in enumerate(mesh.primitives):
            def _get_file_path(stage : str):
                return os.path.join(
                    out_dir,
                    f'{mesh_name}-{primitive_idx}-{stage}.hlsl'
                )
            
            file_path = _get_file_path('VS')
            if not skip_codegen:
                with perf.TimedScope(f'Generating {file_path} ', 'Done'), \
                    open(file_path, 'w') as vs_file:
                    #
                    _impl.generate_vs(vs_file, primitive)
            shaders.append(_VertexShader(file_path))

            file_path = _get_file_path('PS')
            if not skip_codegen:
                with perf.TimedScope(f'Generating {file_path} ', 'Done'), \
                    open(file_path, 'w') as ps_file:
                    #
                    _impl.generate_ps(
                        ps_file,
                        gltf_asset.materials[primitive.material],
                        primitive
                    )
            shaders.append(_PixelShader(file_path))

    log, sys.stdout = sys.stdout, log
    return _AssetResult(log.getvalue(), shaders)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Generate shaders from glTF materials."
    )
    parser.add_argument("--gltf-dir", help = "Path to the source glTF assets")
    parser.add_argument("--out-dir", help = "Path to the output directory")
    parser.add_argument(
        "--compile",
        action = 'store_true',
        help = "Compile the generated shaders with DXC (has to be in PATH)"
    )
    parser.add_argument(
        "--to-glsl",
        action = 'store_true',
        help = "Cross-compile to GLSL with SPIRV-Cross"
    )
    parser.add_argument(
        "--skip-codegen",
        action = 'store_true',
        help = "Assume that sources have been generated and proceed to "
               "compilation."
    )
    parser.add_argument(
        "--serial",
        action = 'store_true',
        help = "Disable parallelization to facilitate debugging."
    )
    args = parser.parse_args()
    
    if not os.path.isdir(args.gltf_dir):
        raise NotADirectoryError(args.gltf_dir)
    
    os.makedirs(args.out_dir, exist_ok = True)

    shaders = []
    if args.serial:
        for gltf_path in pathlib.Path(args.gltf_dir).glob('**/*.gltf'):
            asset_result = _process_asset(
                gltf_file_path = gltf_path,
                out_dir = args.out_dir,
                skip_codegen = args.skip_codegen
            )
            print(asset_result.log)
            shaders += asset_result.shaders
    else:
        with mp.Pool() as pool:
            for asset_result in pool.imap_unordered(
                functools.partial(
                    _process_asset,
                    out_dir = args.out_dir,
                    skip_codegen = args.skip_codegen
                ),
                pathlib.Path(args.gltf_dir).glob('**/*.gltf')
            ):
                print(asset_result.log)
                shaders += asset_result.shaders

    if args.compile:
        print()
        dxc.identify()
        if args.to_glsl:
            spirv_cross.identify()
            glslc.identify()

        if args.serial:
            for shader in shaders:
                log = shader.compile(to_glsl = args.to_glsl)
                print(log, end = '')
        else:
            with mp.Pool() as pool:
                for log in pool.imap_unordered(
                    functools.partial(
                        _Shader.compile,
                        to_glsl = args.to_glsl
                    ),
                    shaders
                ):
                    print(log, end = '')
