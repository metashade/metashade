[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

void clipValue(float value)
{
	clip(value);
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	clipValue(g_f4A.x);
	PsOut result;
	result.color = g_f4B;
	return result;
}

