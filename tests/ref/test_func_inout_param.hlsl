[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

#line 237 "/app/tests/test_functions.py"
void modifyInOut(inout float4 value)
{
#line 240 "/app/tests/test_functions.py"
	value = value + value;
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 243 "/app/tests/test_functions.py"
PsOut main()
{
#line 244 "/app/tests/test_functions.py"
	float4 test_value = g_f4A;
#line 245 "/app/tests/test_functions.py"
	modifyInOut(test_value);
#line 248 "/app/tests/test_functions.py"
	PsOut result;
#line 249 "/app/tests/test_functions.py"
	result.color = test_value;
	return result;
}

