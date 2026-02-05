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

#line 74 "/app/tests/test_if.py"
PsOut main()
{
#line 75 "/app/tests/test_if.py"
	PsOut result;
#line 77 "/app/tests/test_if.py"
	if (g_f4A.x)
	{
#line 78 "/app/tests/test_if.py"
		result.color = g_f4B;
	}
#line 79 "/app/tests/test_if.py"
	else
	{
#line 80 "/app/tests/test_if.py"
		result.color = g_f4D;
	}
	return result;
#line 83 "/app/tests/test_if.py"
	result.color = g_f4C;
	return result;
}

