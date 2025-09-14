float4 add(float4 a, float4 b)
{
	return (a + b);
}

[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 c = add(g_f4A, g_f4B);
	PsOut result;
	result.color = c;
	return result;
}

