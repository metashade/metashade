[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

float4 py_add(float4 a, float4 b)
{
	float4 c = (a + b);
	return c;
}

float4 py_mul(float4 a, float4 b)
{
	float4 c = (a * b);
	return c;
}

float4 py_madd(float4 a, float4 b, float4 c)
{
	float4 d = py_add(a, b);
	float4 e = py_mul(d, c);
	return e;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	float4 c = py_madd(g_f4A, g_f4B, g_f4C);
	PsOut result;
	result.color = c;
	return result;
}

