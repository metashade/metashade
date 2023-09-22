Texture2d g_tColor0;
Sampler g_sColor0;
Texture2d g_tColor1;
Sampler g_sColor1;
Texture2d g_tShadow;
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

