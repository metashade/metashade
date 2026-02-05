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

#line 51 "/app/tests/test_if.py"
PsOut main()
{
#line 52 "/app/tests/test_if.py"
	PsOut result;
#line 54 "/app/tests/test_if.py"
	if (g_f4A.x)
	{
#line 55 "/app/tests/test_if.py"
		result.color = g_f4B;
#line 57 "/app/tests/test_if.py"
		if (g_f4A.y)
		{
#line 58 "/app/tests/test_if.py"
			result.color = g_f4D;
			return result;
		}
		return result;
	}
#line 63 "/app/tests/test_if.py"
	result.color = g_f4C;
	return result;
}

