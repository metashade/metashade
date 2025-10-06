[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

void addOutParam(float4 a, float4 b, out float4 c)
{
	c = (a + b);
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 result_color;
	addOutParam(g_f4A, g_f4B, result_color);
	PsOut result;
	result.color = result_color;
	return result;
}

