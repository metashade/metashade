[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

void modifyInOut(inout float4 value)
{
	value = value + value;
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 test_value = g_f4A;
	modifyInOut(test_value);
	PsOut result;
	result.color = test_value;
	return result;
}

