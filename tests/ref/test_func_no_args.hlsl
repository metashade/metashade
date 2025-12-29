[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

float4 getA0();

float4 getA1();

float4 getA2()
{
	return g_f4A;
}

float4 getA3()
{
	return g_f4A;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	PsOut result;
	result.color = getA2() + getA3();
	return result;
}

