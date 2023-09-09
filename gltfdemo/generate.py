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

import argparse, io, math, os, pathlib, sys
import multiprocessing as mp
from collections import namedtuple
from pygltflib import GLTF2

from metashade.hlsl.sm6 import ps_6_0, vs_6_0
import metashade.hlsl.common as hlsl_common
import metashade.util as util

def _generate_vs_out(sh, primitive):
    with sh.vs_output('VsOut') as VsOut:
        VsOut.SV_Position('Pclip', sh.Vector4f)
        
        VsOut.texCoord('Pw', sh.Point3f)
        VsOut.texCoord('Nw', sh.Vector3f)

        if primitive.attributes.TANGENT is not None:
            VsOut.texCoord('Tw', sh.Vector3f)
            VsOut.texCoord('Bw', sh.Vector3f)

        VsOut.texCoord('uv0', sh.Point2f)

        if primitive.attributes.COLOR_0 is not None:
            VsOut.color('rgbaColor0', sh.RgbaF)

def _generate_per_frame_uniform_buffer(sh):
    sh.struct('Light')(
        VpXf = sh.Matrix4x4f,
        ViewXf = sh.Matrix4x4f,
        v3DirectionW = sh.Vector3f,
        fRange = sh.Float,
        rgbColor = sh.RgbF,
        fIntensity = sh.Float,
        Pw = sh.Point3f,
        fInnerConeCos = sh.Float,
        fOuterConeCos = sh.Float,
        type_ = sh.Float, # should be an int, but we assume a spotlight anyway
        fDepthBias = sh.Float,
        iShadowMap = sh.Float # should be an int, unused for now
    )

    with sh.uniform_buffer(register = 0, name = 'cbPerFrame'):
        sh.uniform('g_VpXf', sh.Matrix4x4f)
        sh.uniform('g_prevVpXf', sh.Matrix4x4f)
        sh.uniform('g_VpIXf', sh.Matrix4x4f)
        sh.uniform('g_cameraPw', sh.Point3f)
        sh.uniform('g_cameraPw_fPadding', sh.Float)
        sh.uniform('g_fIblFactor', sh.Float)
        sh.uniform('g_fPerFrameEmissiveFactor', sh.Float)
        sh.uniform('g_fInvScreenResolution', sh.Float2)
        sh.uniform('g_f4WireframeOptions', sh.Float4)
        sh.uniform('g_f2MCameraCurrJitter', sh.Float2)
        sh.uniform('g_f2MCameraPrevJitter', sh.Float2)

        # should be an array
        for light_idx in range(0, 80):
            sh.uniform(f'g_light{light_idx}', sh.Light)

        sh.uniform('g_nLights', sh.Float)   # should be int
        sh.uniform('g_lodBias', sh.Float)

def _generate_per_object_uniform_buffer(sh, is_ps : bool):
    if is_ps:
        # https://github.com/ppenenko/Cauldron/blob/master/src/DX12/shaders/PBRPixelParams.hlsl#L33
        sh.struct('PbrFactors')(
            rgbaEmissive = sh.RgbaF,

            # pbrMetallicRoughness
            rgbaBaseColor = sh.RgbaF,
            fMetallic = sh.Float,
            fRoughness = sh.Float,

            f2Padding = sh.Float2,

            # KHR_materials_pbrSpecularGlossiness
            rgbaDiffuse = sh.RgbaF,
            rgbSpecular = sh.RgbF,
            fGlossiness = sh.Float
        )

    with sh.uniform_buffer(register = 1, name = 'cbPerObject'):
        sh.uniform('g_WorldXf', sh.Matrix3x4f)
        sh.uniform('g_prevWorldXf', sh.Matrix3x4f)
        if is_ps:
            sh.uniform('g_perObjectPbrFactors', sh.PbrFactors)

_vs_main = 'mainVS'

def _generate_vs(vs_file, primitive):
    sh = vs_6_0.Generator(
        vs_file,
        # the host app supplies transposed matrix uniforms
        matrix_post_multiplication = True
    )

    _generate_per_frame_uniform_buffer(sh)
    _generate_per_object_uniform_buffer(sh, is_ps = False)

    attributes = primitive.attributes

    with sh.vs_input('VsIn') as VsIn:
        if attributes.POSITION is None:
            raise RuntimeError('POSITION attribute is mandatory')
        VsIn.position('Pobj', sh.Point3f)

        if attributes.NORMAL is not None:
            VsIn.normal('Nobj', sh.Vector3f)

        if attributes.TANGENT is not None:
            VsIn.tangent('Tobj', sh.Vector4f)

        if attributes.TEXCOORD_0 is not None:
            VsIn.texCoord('uv0', sh.Point2f)

        if attributes.TEXCOORD_1 is not None:
            VsIn.texCoord('uv1', sh.Point2f)

        if attributes.COLOR_0 is not None:
            VsIn.color('rgbaColor0', sh.RgbaF)

        if attributes.JOINTS_0 is not None:
            raise RuntimeError('Unsupported attribute JOINTS_0')

        if attributes.WEIGHTS_0 is not None:
            raise RuntimeError('Unsupported attribute WEIGHTS_0')

    _generate_vs_out(sh, primitive)

    with sh.main(_vs_main, sh.VsOut)(vsIn = sh.VsIn):
        sh.Pw = sh.g_WorldXf.xform(sh.vsIn.Pobj)
        sh.vsOut = sh.VsOut()
        sh.vsOut.Pclip = sh.g_VpXf.xform(sh.Pw)
        sh.vsOut.Pw = sh.Pw.xyz
        sh.vsOut.Nw = sh.g_WorldXf.xform(sh.vsIn.Nobj).xyz.normalize()
        
        if hasattr(sh.vsIn, 'Tobj'):
            sh.vsOut.Tw = sh.g_WorldXf.xform(sh.vsIn.Tobj.xyz).xyz.normalize()
            sh.vsOut.Bw = sh.vsOut.Nw.cross(sh.vsOut.Tw) * sh.vsIn.Tobj.w

        # Simple passthrough for these attributes
        for attr_name in ('uv0', 'uv1', 'rgbaColor0'):
            if hasattr(sh.vsIn, attr_name):
                setattr(sh.vsOut, attr_name, getattr(sh.vsIn, attr_name))

        sh.return_(sh.vsOut)

_ps_main = 'mainPS'

def _generate_ps(ps_file, material, primitive):
    sh = ps_6_0.Generator(
        ps_file,
        # the host app supplies transposed matrix uniforms
        matrix_post_multiplication = True
    )

    _generate_per_frame_uniform_buffer(sh)
    _generate_per_object_uniform_buffer(sh, is_ps = True)

    _generate_vs_out(sh, primitive)

    with sh.ps_output('PsOut') as PsOut:
        PsOut.SV_Target('rgbaColor', sh.RgbaF)

    texture_dict = dict()
    _TextureRecord = namedtuple('_TextureRecord', 'gltf_texture texel_type')

    def _add_texture(parent, name: str, texel_type = None):
        gltf_texture = getattr(parent, name + 'Texture')
        if gltf_texture is not None:
            texture_dict[name] = _TextureRecord(gltf_texture, texel_type)

    _add_texture(material, 'normal', sh.Vector4f)
    _add_texture(material, 'occlusion')
    _add_texture(material, 'emissive', sh.RgbaF)

    if material.pbrMetallicRoughness is not None:
        _add_texture(
            material.pbrMetallicRoughness, 'baseColor', sh.RgbaF
        )
        _add_texture(
            material.pbrMetallicRoughness,
            'metallicRoughness',
            sh.RgbaF
        )
    elif material.extensions is not None:
        specularGlossiness = \
            material.extensions.KHR_materials_pbrSpecularGlossiness
        if specularGlossiness is not None:
            _add_texture(specularGlossiness, 'diffuse', sh.RgbaF)
            _add_texture(specularGlossiness, 'specularGlossiness')
            assert (False,
                'KHR_materials_pbrSpecularGlossiness is not implemented yet, '
                'see https://github.com/ppenenko/metashade/issues/18'
            )
    
    def _get_texture_uniform_name(name: str) -> str:
        return 'g_t' + name[0].upper() + name[1:]
    
    def _get_sampler_uniform_name(name: str) -> str:
        return 'g_s' + name[0].upper() + name[1:]

    # We're sorting material textures by name
    for texture_idx, (texture_name, texture_record) in enumerate(
        sorted(texture_dict.items())
    ):  
        sh.combined_sampler_2d(
            texture_name = _get_texture_uniform_name(texture_name),
            texture_register = texture_idx,
            sampler_name = _get_sampler_uniform_name(texture_name),
            sampler_register = texture_idx,
            texel_type = texture_record.texel_type
        )

    sh.combined_sampler_2d(
        texture_name = 'shadowMap',
        texture_register = 9,
        sampler_name = 'shadowSampler',
        sampler_register = 9,
        cmp = True
    )

    def _sample_texture(texture_name : str):
        texture_record = texture_dict.get(texture_name)
        if texture_record is None:
            return None

        uv_set_idx = texture_record.gltf_texture.texCoord
        if uv_set_idx is None:
            uv_set_idx = 0

        uv = getattr(sh.psIn, f'uv{uv_set_idx}')
        sampler = getattr(sh, _get_sampler_uniform_name(texture_name))

        sample = sampler(uv, lod_bias = sh.g_lodBias)
        sample_var_name = texture_name + 'Sample'
        setattr(sh, sample_var_name, sample)
        return getattr(sh, sample_var_name)

    sh.struct('PbrParams')(
        rgbDiffuse = sh.RgbF,
        rgbF0 = sh.RgbF,
        fPerceptualRoughness = sh.Float,
        fOpacity = sh.Float
    )

    with sh.function('metallicRoughness', sh.PbrParams)(psIn = sh.VsOut):
        sh.rgbaBaseColor = sh.g_sBaseColor(sh.psIn.uv0) \
            * sh.g_perObjectPbrFactors.rgbaBaseColor
        if hasattr(sh.psIn, 'rgbaColor0'):
            sh.rgbaBaseColor *= sh.psIn.rgbaColor0

        if material.alphaMode == 'BLEND':
            sh.rgbaBaseColor.a.clip()
        elif material.alphaMode == 'MASK':
            sh.fAlphaCutoff = sh.Float(float(material.alphaCutoff))
            (sh.rgbaBaseColor.a - sh.fAlphaCutoff).clip()
        
        sh.fPerceptualRoughness = sh.g_perObjectPbrFactors.fRoughness
        sh.fMetallic = sh.g_perObjectPbrFactors.fMetallic

        metallicRoughnessSample = _sample_texture('metallicRoughness')
        if metallicRoughnessSample is not None:
            sh.fPerceptualRoughness *= metallicRoughnessSample.g
            sh.fMetallic *= metallicRoughnessSample.b

        sh.fMetallic = sh.fMetallic.saturate()
        sh.fMinF0 = sh.Float(0.04)

        sh.pbrParams = sh.PbrParams()
        sh.pbrParams.rgbDiffuse = sh.rgbaBaseColor.rgb \
            * (sh.Float(1.0) - sh.fMinF0) \
            * (sh.Float(1.0) - sh.fMetallic)
        sh.pbrParams.rgbF0 = sh.RgbF(sh.fMetallic).lerp(
            sh.RgbF(sh.fMinF0), sh.rgbaBaseColor.rgb
        )
        sh.pbrParams.fPerceptualRoughness = sh.fPerceptualRoughness.saturate()
        sh.pbrParams.fOpacity = sh.rgbaBaseColor.a
        sh.return_(sh.pbrParams)

    with sh.function('D_Ggx', sh.Float)(
        NdotH = sh.Float, fAlphaRoughness = sh.Float
    ):
        sh.fASqr = sh.fAlphaRoughness * sh.fAlphaRoughness
        sh.fF = (sh.NdotH * sh.fASqr - sh.NdotH) * sh.NdotH + sh.Float(1.0)
        sh.return_(
            sh.fASqr / (sh.Float(math.pi) * sh.fF * sh.fF )
        )

    with sh.function('F_Schlick', sh.RgbF)(LdotH = sh.Float, rgbF0 = sh.RgbF):
        sh.return_(
            sh.rgbF0 + (sh.RgbF(1.0) - sh.rgbF0) \
                * (sh.Float(1.0) - sh.LdotH).pow(sh.Float(5.0))
        )

    with sh.function('V_SmithGgxCorrelated', sh.Float)(
        NdotV = sh.Float, NdotL = sh.Float, fAlphaRoughness = sh.Float
    ):
        sh.fASqr = sh.fAlphaRoughness * sh.fAlphaRoughness
        sh.fGgxL = sh.NdotV * (
            (sh.NdotL - sh.NdotL * sh.fASqr) * sh.NdotL + sh.fASqr
        ).sqrt()
        sh.fGgxV = sh.NdotL * (
            (sh.NdotV - sh.NdotV * sh.fASqr) + sh.NdotV + sh.fASqr
        ).sqrt()
        sh.return_(sh.Float(0.5) / (sh.fGgxL + sh.fGgxV))

    with sh.function('Fd_Lambert', sh.Float)():
        sh.return_( sh.Float( 1.0 / math.pi ) )

    with sh.function('pbrBrdf', sh.RgbF)(
        L = sh.Vector3f, N = sh.Vector3f, V = sh.Vector3f,
        pbrParams = sh.PbrParams
    ):
        sh.H = (sh.V + sh.L).normalize()

        sh.NdotV = sh.N.dot(sh.V).abs()

        for first, second in (('N', 'L'), ('N', 'H'), ('L', 'H')):
            setattr(
                sh,
                f'{first}dot{second}',
                getattr(sh, first).dot(getattr(sh, second)).saturate()
            )

        sh.fAlphaRoughness = sh.pbrParams.fPerceptualRoughness \
            * sh.pbrParams.fPerceptualRoughness

        sh.fD = sh.D_Ggx(
            NdotH = sh.NdotH,
            fAlphaRoughness = sh.fAlphaRoughness
        )
        sh.rgbF = sh.F_Schlick(
            LdotH = sh.LdotH, rgbF0 = sh.pbrParams.rgbF0
        )
        sh.fV = sh.V_SmithGgxCorrelated(
            NdotV = sh.NdotV,
            NdotL = sh.NdotL,
            fAlphaRoughness = sh.fAlphaRoughness
        )

        sh.rgbFr = (sh.fD * sh.fV) * sh.rgbF
        sh.rgbFd = sh.pbrParams.rgbDiffuse * sh.Fd_Lambert()
        
        sh.return_(sh.NdotL * (sh.rgbFr + sh.rgbFd))

    with sh.function('getRangeAttenuation', sh.Float)(
        light = sh.Light, d = sh.Float
    ):
        # https://github.com/KhronosGroup/glTF/blob/master/extensions/2.0/Khronos/KHR_lights_punctual/README.md#range-property
        # TODO: handle undefined/unlimited ranges
        sh.return_(
            (sh.d / sh.light.fRange).lerp(sh.Float(1), sh.Float(0)).saturate()
        )

    with sh.function('getSpotShadow', sh.Float)(
        light = sh.Light, Pw = sh.Point3f
    ):
        sh.p4Shadow = sh.light.VpXf.xform(sh.Pw)
        sh.p4Shadow.xyz /= sh.p4Shadow.w
        
        sh.uvShadow = (
            sh.Point2f(1.0) + sh.Point2f((sh.p4Shadow.x, -sh.p4Shadow.y))
        ) * sh.Float(0.5)
        sh.fCompareValue = sh.p4Shadow.z - sh.light.fDepthBias
        sh.fShadowSample = sh.shadowSampler(
            sh.uvShadow, cmp_value = sh.fCompareValue, lod = 0
        )
        sh.return_(sh.fShadowSample)

    with sh.function('applySpotLight', sh.RgbF)(
        light = sh.Light,
        Nw = sh.Vector3f,
        Vw = sh.Vector3f,
        Pw = sh.Point3f,
        pbrParams = sh.PbrParams
    ):
        sh.Lw = sh.light.Pw - sh.Pw
        sh.fRangeAttenuation = sh.getRangeAttenuation(
            light = sh.light, d = sh.Lw.length()
        )
        sh.Lw = sh.Lw.normalize()

        sh.DdotL = sh.light.v3DirectionW.dot(sh.Lw)
        sh.fSpotAttenuation = sh.DdotL.smoothstep(
            sh.light.fOuterConeCos, sh.light.fInnerConeCos
        )

        sh.fLightAttenuation = sh.fRangeAttenuation * sh.fSpotAttenuation
        sh.rgbLightColor = sh.light.fIntensity * sh.light.rgbColor
        sh.fShadow = sh.getSpotShadow(light = sh.light, Pw = sh.Pw)

        sh.return_( sh.pbrBrdf(
            L = sh.Lw,
            N = sh.Nw,
            V = sh.Vw,
            pbrParams = sh.pbrParams
        ) * sh.fLightAttenuation * sh.rgbLightColor * sh.fShadow )

    with sh.main(_ps_main, sh.PsOut)(psIn = sh.VsOut):
        normalSample = _sample_texture('normal')
        if (normalSample is not None
            and primitive.attributes.TANGENT is not None
        ):
            sh.tbn = sh.Matrix3x3f(rows = (sh.psIn.Tw, sh.psIn.Bw, sh.psIn.Nw))
            sh.tbn = sh.tbn.transpose()
            sh.Nw = sh.tbn.xform(2.0 * normalSample.xyz - sh.Vector3f(1.0))
        else:
            print ('TODO: https://github.com/ppenenko/metashade/issues/19')
            sh.Nw = sh.psIn.Nw
        sh.Nw = sh.Nw.normalize()

        sh.Vw = (sh.g_cameraPw - sh.psIn.Pw).normalize()
        sh.pbrParams = sh.metallicRoughness(psIn = sh.psIn)
        
        sh.psOut = sh.PsOut()
        sh.psOut.rgbaColor.rgb = sh.applySpotLight(
            light = sh.g_light0,
            Pw = sh.psIn.Pw,
            Nw = sh.Nw,
            Vw = sh.Vw,
            pbrParams = sh.pbrParams
        )
        
        sh.psOut.rgbaColor.a = sh.pbrParams.fOpacity

        aoSample = _sample_texture('occlusion')
        if aoSample is not None:
            sh.psOut.rgbaColor.rgb *= aoSample.x

        sh.rgbEmissive = sh.g_perObjectPbrFactors.rgbaEmissive.rgb * sh.g_fPerFrameEmissiveFactor
        emissiveSample = _sample_texture('emissive')
        if emissiveSample is not None:
            sh.rgbEmissive *= emissiveSample.rgb
        sh.psOut.rgbaColor.rgb += sh.rgbEmissive

        sh.return_(sh.psOut)

class _Shader:
    def __init__(self, file_path):
        self._file_path = file_path

    @staticmethod
    def _get_entry_point_name():
        return None
    
    @staticmethod
    def _get_profile():
        return None

    def compile(self) -> str:
        log = io.StringIO()
        sys.stdout = log
        hlsl_common.compile(
            path = self._file_path,
            entry_point_name = self._get_entry_point_name(),
            profile = self._get_profile()
        )
        return log.getvalue()

class _VertexShader(_Shader):
    @staticmethod
    def _get_entry_point_name():
        return _vs_main
    
    @staticmethod
    def _get_profile():
        return 'vs_6_0'
    
class _PixelShader(_Shader):
    @staticmethod
    def _get_entry_point_name():
        return _ps_main
    
    @staticmethod
    def _get_profile():
        return 'ps_6_0'

_AssetResult = namedtuple('_AssetResult', 'log shaders')

class _AssetProcessor:
    def __init__(self, out_dir):
        self._out_dir = out_dir

    def __call__(self, gltf_file_path : str) -> _AssetResult:
        shaders = []
        sys.stdout = io.StringIO()
        
        with util.TimedScope(f'Loading glTF asset {gltf_file_path} '):
            gltf_asset = GLTF2().load(gltf_file_path)

        for mesh_idx, mesh in enumerate(gltf_asset.meshes):
            mesh_name = ( mesh.name if mesh.name is not None
                else f'UnnamedMesh{mesh_idx}'
            )

            for primitive_idx, primitive in enumerate(mesh.primitives):
                def _get_file_path(stage : str):
                    return os.path.join(
                        self._out_dir,
                        f'{mesh_name}-{primitive_idx}-{stage}.hlsl'
                    )
                
                file_path = _get_file_path('VS')
                with util.TimedScope(f'Generating {file_path} ', 'Done'), \
                    open(file_path, 'w') as vs_file:
                    #
                    _generate_vs(vs_file, primitive)
                shaders.append(_VertexShader(file_path))

                file_path = _get_file_path('PS')
                with util.TimedScope(f'Generating {file_path} ', 'Done'), \
                    open(file_path, 'w') as ps_file:
                    #
                    _generate_ps(
                        ps_file,
                        gltf_asset.materials[primitive.material],
                        primitive
                    )
                shaders.append(_PixelShader(file_path))
        return _AssetResult(sys.stdout.getvalue(), shaders)

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
    args = parser.parse_args()
    
    if not os.path.isdir(args.gltf_dir):
        raise NotADirectoryError(args.gltf_dir)
    
    os.makedirs(args.out_dir, exist_ok = True)

    shaders = []
    with mp.Pool() as pool:
        for asset_result in pool.imap_unordered(
            _AssetProcessor(args.out_dir),
            pathlib.Path(args.gltf_dir).glob('**/*.gltf')
        ):
            print(asset_result.log)
            shaders += asset_result.shaders

    if args.compile:
        with mp.Pool() as pool:
            for compilation_log in pool.imap_unordered(_Shader.compile, shaders):
                print(compilation_log)
