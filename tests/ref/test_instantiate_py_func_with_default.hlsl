[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

// Function with default parameter value.
//
float4 _py_add_with_default(float4 a, float4 b)
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
	float4 c = _py_add_with_default(g_f4A, float4(1.0, 1.0, 1.0, 1.0));
	float4 c2 = _py_add_with_default(g_f4A, g_f4B);
	PsOut result;
	result.color = c + c2;
	return result;
}

