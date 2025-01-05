cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

float4 func(float4 a, float3 c);

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	PsOut result;
	result.color = func(g_f4A, g_f3C);
	return result;
}

