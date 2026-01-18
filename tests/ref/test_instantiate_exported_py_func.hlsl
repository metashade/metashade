[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

#line 74 "/app/tests/test_instantiate.py"
float4 py_add(float4 a, float4 b)
{
#line 19 "/app/tests/_exports.py"
	float4 c = a + b;
	return c;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 76 "/app/tests/test_instantiate.py"
PsOut main()
{
#line 77 "/app/tests/test_instantiate.py"
	float4 c = py_add(g_f4A, g_f4B);
#line 80 "/app/tests/test_instantiate.py"
	PsOut result;
#line 81 "/app/tests/test_instantiate.py"
	result.color = c;
	return result;
}

