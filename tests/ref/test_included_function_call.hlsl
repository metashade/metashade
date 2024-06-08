#include "include/add.hlsl"
float4 add(float4 a, float4 b);

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

PsOut psMain()
{
	PsOut result;
	result.color = add(g_f4A, g_f4B);
	return result;
}

