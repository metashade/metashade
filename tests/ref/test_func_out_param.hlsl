[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

#line 211 "/app/tests/test_functions.py"
void addOutParam(float4 a, float4 b, out float4 c)
{
#line 214 "/app/tests/test_functions.py"
	c = a + b;
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 217 "/app/tests/test_functions.py"
PsOut main()
{
#line 218 "/app/tests/test_functions.py"
	float4 result_color;
#line 219 "/app/tests/test_functions.py"
	addOutParam(g_f4A, g_f4B, result_color);
#line 224 "/app/tests/test_functions.py"
	PsOut result;
#line 225 "/app/tests/test_functions.py"
	result.color = result_color;
	return result;
}

