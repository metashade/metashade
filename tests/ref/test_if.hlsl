cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
	float4 g_f4D;
};

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 33 "/app/tests/test_if.py"
PsOut main()
{
#line 34 "/app/tests/test_if.py"
	PsOut result;
#line 36 "/app/tests/test_if.py"
	if (g_f4A.x)
	{
#line 37 "/app/tests/test_if.py"
		result.color = g_f4B;
		return result;
	}
#line 40 "/app/tests/test_if.py"
	result.color = g_f4C;
	return result;
}

