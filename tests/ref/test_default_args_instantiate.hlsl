[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

float4 addDefInst(float4 a, float4 b)
{
	float4 c = a + b;
	return c;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 c = addDefInst(g_f4A, float4(1.0, 1.0, 1.0, 1.0));
	float4 c2 = addDefInst(g_f4A, g_f4B);
	PsOut result;
	result.color = c + c2;
	return result;
}

