cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut psMain()
{
	PsOut result;
	if (g_f4A.x)
	{
		result.color = g_f4B;
		return result;
	}

	result.color = g_f4C;
	return result;
}

