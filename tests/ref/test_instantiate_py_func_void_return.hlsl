[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

void _py_clip(float value)
{
	clip(value);
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	_py_clip(g_f4A.x);
	PsOut result;
	result.color = g_f4B;
	return result;
}

