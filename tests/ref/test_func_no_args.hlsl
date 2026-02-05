[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

#line 190 "/app/tests/test_functions.py"
float4 getA0();

#line 191 "/app/tests/test_functions.py"
float4 getA1();

#line 193 "/app/tests/test_functions.py"
float4 getA2()
{
	return g_f4A;
}

#line 196 "/app/tests/test_functions.py"
float4 getA3()
{
	return g_f4A;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 199 "/app/tests/test_functions.py"
PsOut main()
{
#line 200 "/app/tests/test_functions.py"
	PsOut result;
#line 201 "/app/tests/test_functions.py"
	result.color = getA2() + getA3();
	return result;
}

