[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	bool g_flag;
	float4 g_f4A;
	float4 g_f4B;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	PsOut result;
	if (g_flag)
	{
		result.color = g_f4A;
	}
	else
	{
		result.color = g_f4B;
	}
	return result;
}

