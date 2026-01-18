#line 21 "/app/tests/test_dtypes.py"
float test()
{
#line 22 "/app/tests/test_dtypes.py"
	float4 f4A = 1.0.xxxx;
#line 23 "/app/tests/test_dtypes.py"
	float4 f4B = 0.0.xxxx - f4A;
#line 25 "/app/tests/test_dtypes.py"
	float3 f3A = 0.0.xxx;
#line 26 "/app/tests/test_dtypes.py"
	float3 f3B = f3A + 1.0.xxx;
#line 28 "/app/tests/test_dtypes.py"
	float2 f2A = 0.6578467.xx;
#line 29 "/app/tests/test_dtypes.py"
	float2 f2B = 0.4235.xx * f2A;
#line 31 "/app/tests/test_dtypes.py"
	float fA = 1.0;
#line 32 "/app/tests/test_dtypes.py"
	float fB = 2.0 + fA;
	return ((f4B.w + f3B.z) + f2B.y) + fB;
}

#line 20 "/app/tests/test_dtypes.py"
void main()
{
}

