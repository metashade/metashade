Texture2D colorTexture0 : register(t0);
SamplerState colorSampler0 : register(s1);

Texture2D colorTexture1 : register(t1);
SamplerState colorSampler1 : register(s0);

Texture2D shadowMap : register(t2);
SamplerComparisonState shadowSampler : register(s2);

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
	float4 rgbaSample = colorTexture1.Sample(colorSampler1, psIn.uv0);
	float fShadowSample0 = shadowMap.SampleCmp(shadowSampler, psIn.uv0, 0.5).r;
	float fShadowSample1 = shadowMap.SampleCmpLevelZero(shadowSampler, psIn.uv0, 0.1).r;
	psOut.color = ((rgbaSample * fShadowSample0) * fShadowSample1);
	return psOut;
}

