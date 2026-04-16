[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

float4 addDefault(float4 a, float4 b)
{
	return a + b;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 c = addDefault(g_f4A, float4(1.0, 1.0, 1.0, 1.0));
	float4 c2 = addDefault(g_f4A, g_f4B);
	PsOut result;
	result.color = c + c2;
	return result;
}

