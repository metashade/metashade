#version 450
#line 21 "/app/tests/test_dtypes.py"
float test()
{
#line 22 "/app/tests/test_dtypes.py"
	vec4 f4A = vec4(1.0);
#line 23 "/app/tests/test_dtypes.py"
	vec4 f4B = vec4(0.0) - f4A;
#line 25 "/app/tests/test_dtypes.py"
	vec3 f3A = vec3(0.0);
#line 26 "/app/tests/test_dtypes.py"
	vec3 f3B = f3A + vec3(1.0);
#line 28 "/app/tests/test_dtypes.py"
	vec2 f2A = vec2(0.6578467);
#line 29 "/app/tests/test_dtypes.py"
	vec2 f2B = vec2(0.4235) * f2A;
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

