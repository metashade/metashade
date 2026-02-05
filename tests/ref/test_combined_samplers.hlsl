Texture2D g_tColor0 : register(t0);
SamplerState g_sColor0 : register(s1);
Texture2D g_tColor1 : register(t1);
SamplerState g_sColor1 : register(s0);
Texture2D g_tShadow : register(t2);
SamplerComparisonState g_sShadow : register(s2);
Texture1D g_t1d : register(t3);
Texture3D g_t3d : register(t4);
TextureCube g_tCube : register(t5);
struct VsOut
{
	float2 uv0 : TEXCOORD;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 40 "/app/tests/test_samplers.py"
PsOut main(VsOut psIn)
{
#line 41 "/app/tests/test_samplers.py"
	PsOut psOut;
#line 43 "/app/tests/test_samplers.py"
	float4 rgbaSample0 = g_tColor1.Sample(g_sColor1, psIn.uv0);
#line 46 "/app/tests/test_samplers.py"
	float4 rgbaSample1 = g_tColor1.SampleLevel(g_sColor1, psIn.uv0, 0.9);
#line 47 "/app/tests/test_samplers.py"
	float4 rgbaSample2 = g_tColor1.SampleBias(g_sColor1, psIn.uv0, 0.1);
#line 49 "/app/tests/test_samplers.py"
	float fShadowSample0 = g_tShadow.SampleCmp(g_sShadow, psIn.uv0, 0.5).r;
#line 53 "/app/tests/test_samplers.py"
	float fShadowSample1 = g_tShadow.SampleCmpLevelZero(g_sShadow, psIn.uv0, 0.1).r;
#line 59 "/app/tests/test_samplers.py"
	float4 f1dSample = g_t1d.Sample(g_sColor1, psIn.uv0.x);
#line 60 "/app/tests/test_samplers.py"
	float4 f3dSample = g_t3d.Sample(g_sColor1, 0.5.xxx);
#line 61 "/app/tests/test_samplers.py"
	float4 f3CubeSample = g_tCube.Sample(g_sColor1, 0.5.xxx);
#line 63 "/app/tests/test_samplers.py"
	psOut.color = ((((((rgbaSample0 * rgbaSample1) * rgbaSample2) * fShadowSample0) * fShadowSample1) * f1dSample) * f3dSample) * f3CubeSample;
	return psOut;
}

