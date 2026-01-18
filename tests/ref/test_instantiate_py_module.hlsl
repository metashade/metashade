[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

#line 94 "/app/tests/test_instantiate.py"
float4 py_add(float4 a, float4 b)
{
#line 19 "/app/tests/_exports.py"
	float4 c = a + b;
	return c;
}

#line 94 "/app/tests/test_instantiate.py"
float4 py_mul(float4 a, float4 b)
{
#line 24 "/app/tests/_exports.py"
	float4 c = a * b;
	return c;
}

#line 94 "/app/tests/test_instantiate.py"
float4 py_madd(float4 a, float4 b, float4 c)
{
#line 29 "/app/tests/_exports.py"
	float4 d = py_add(a, b);
#line 30 "/app/tests/_exports.py"
	float4 e = py_mul(d, c);
	return e;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 96 "/app/tests/test_instantiate.py"
PsOut main()
{
#line 97 "/app/tests/test_instantiate.py"
	float4 c = py_madd(g_f4A, g_f4B, g_f4C);
#line 102 "/app/tests/test_instantiate.py"
	PsOut result;
#line 103 "/app/tests/test_instantiate.py"
	result.color = c;
	return result;
}

