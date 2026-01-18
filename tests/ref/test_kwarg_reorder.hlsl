[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

#line 79 "/app/tests/test_functions.py"
float4 func(float4 a, float3 c);

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 81 "/app/tests/test_functions.py"
PsOut main()
{
#line 82 "/app/tests/test_functions.py"
	PsOut result;
#line 83 "/app/tests/test_functions.py"
	result.color = func(g_f4A, g_f3C);
	return result;
}

