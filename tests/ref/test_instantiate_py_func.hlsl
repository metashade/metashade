[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

#line 54 "/app/tests/test_instantiate.py"
float4 _py_add(float4 a, float4 b)
{
#line 18 "/app/tests/test_instantiate.py"
	float4 c = a + b;
	return c;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 56 "/app/tests/test_instantiate.py"
PsOut main()
{
#line 57 "/app/tests/test_instantiate.py"
	float4 c = _py_add(g_f4A, g_f4B);
#line 60 "/app/tests/test_instantiate.py"
	PsOut result;
#line 61 "/app/tests/test_instantiate.py"
	result.color = c;
	return result;
}

