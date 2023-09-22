Texture2D g_tColor0 : register(t0);
SamplerState g_sColor0 : register(s1);
Texture2D g_tColor1 : register(t1);
SamplerState g_sColor1 : register(s0);
Texture2D g_tShadow : register(t2);
struct VsOut
{
	float2 uv0 : TEXCOORD;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut psMain(VsOut psIn)
{
	PsOut psOut;
	float4 rgbaSample0 = g_tColor1.Sample(g_sColor1, psIn.uv0);
	float4 rgbaSample1 = g_tColor1.SampleLevel(g_sColor1, psIn.uv0, 0.9);
	float4 rgbaSample2 = g_tColor1.SampleBias(g_sColor1, psIn.uv0, 0.1);
	psOut.color = ((rgbaSample0 * rgbaSample1) * rgbaSample2);
	return psOut;
}

