#line 21 "/app/tests/test_vector_init.py"
float vector_init()
{
#line 22 "/app/tests/test_vector_init.py"
	float f = 1;
#line 24 "/app/tests/test_vector_init.py"
	float2 f2 = f.xx;
#line 25 "/app/tests/test_vector_init.py"
	f2 = 2.xx;
#line 26 "/app/tests/test_vector_init.py"
	f2 = 0.xx;
#line 27 "/app/tests/test_vector_init.py"
	f2 = float2(0, 1);
#line 28 "/app/tests/test_vector_init.py"
	f2 = float2(3, 4);
#line 29 "/app/tests/test_vector_init.py"
	f2 = float2(5, 6);
#line 30 "/app/tests/test_vector_init.py"
	f2 = float2(f, 7);
#line 31 "/app/tests/test_vector_init.py"
	f2 = float2(8, 9);
#line 33 "/app/tests/test_vector_init.py"
	float3 f3 = f.xxx;
#line 34 "/app/tests/test_vector_init.py"
	f3 = 0.xxx;
#line 35 "/app/tests/test_vector_init.py"
	f3 = 2.xxx;
#line 36 "/app/tests/test_vector_init.py"
	f3 = float3(0, 1, 2);
#line 37 "/app/tests/test_vector_init.py"
	f3 = float3(f, 3, 4.1);
#line 39 "/app/tests/test_vector_init.py"
	float3 p3 = f.xxx;
#line 40 "/app/tests/test_vector_init.py"
	p3 = 2.xxx;
#line 41 "/app/tests/test_vector_init.py"
	p3 = 0.xxx;
#line 42 "/app/tests/test_vector_init.py"
	p3 = float3(0, 1, 0.5);
#line 43 "/app/tests/test_vector_init.py"
	p3 = float3(0.1, f, 3);
#line 45 "/app/tests/test_vector_init.py"
	float4 v4 = f.xxxx;
#line 46 "/app/tests/test_vector_init.py"
	v4 = 2.xxxx;
#line 47 "/app/tests/test_vector_init.py"
	v4 = 0.xxxx;
#line 48 "/app/tests/test_vector_init.py"
	v4 = float4(0, 1, 0.5, 1.0);
#line 49 "/app/tests/test_vector_init.py"
	v4 = float4(0.1, f, 3, 1.0);
#line 51 "/app/tests/test_vector_init.py"
	float3 rgb = f.xxx;
#line 52 "/app/tests/test_vector_init.py"
	rgb = 2.xxx;
#line 53 "/app/tests/test_vector_init.py"
	rgb = 0.xxx;
#line 54 "/app/tests/test_vector_init.py"
	rgb = float3(0, 1, 0.5);
#line 55 "/app/tests/test_vector_init.py"
	rgb = float3(0.1, f, 3);
#line 57 "/app/tests/test_vector_init.py"
	float4 rgba = f.xxxx;
#line 58 "/app/tests/test_vector_init.py"
	rgba = 2.xxxx;
#line 59 "/app/tests/test_vector_init.py"
	rgba = 0.xxxx;
#line 60 "/app/tests/test_vector_init.py"
	rgba = float4(0, 1, 0.5, 1.0);
#line 61 "/app/tests/test_vector_init.py"
	rgba = float4(0.1, f, 3, 1.0);
#line 62 "/app/tests/test_vector_init.py"
	rgba = float4(rgb, 0.0);
	return f;
}

#line 20 "/app/tests/test_vector_init.py"
void main()
{
}

