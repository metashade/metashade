[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float3 g_f3C;
};

#line 172 "/app/tests/test_functions.py"
void clipValue(float value)
{
	clip(value);
	return;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 176 "/app/tests/test_functions.py"
PsOut main()
{
#line 179 "/app/tests/test_functions.py"
	clipValue(g_f4A.x);
#line 181 "/app/tests/test_functions.py"
	PsOut result;
#line 182 "/app/tests/test_functions.py"
	result.color = g_f4B;
	return result;
}

