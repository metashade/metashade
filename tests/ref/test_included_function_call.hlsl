#include "include/add.hlsl"
#line 27 "/app/tests/test_functions.py"
float4 add(float4 a, float4 b);

[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 55 "/app/tests/test_functions.py"
PsOut main()
{
#line 56 "/app/tests/test_functions.py"
	float4 c = add(g_f4A, g_f4B);
#line 59 "/app/tests/test_functions.py"
	PsOut result;
#line 60 "/app/tests/test_functions.py"
	result.color = c;
	return result;
}

