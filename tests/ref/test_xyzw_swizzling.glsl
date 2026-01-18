#version 450
#line 33 "/app/tests/test_swizzling.py"
float xyzw_swizzle(vec3 f3In, vec4 f4In)
{
#line 36 "/app/tests/test_swizzling.py"
	float x = f3In.x;
#line 37 "/app/tests/test_swizzling.py"
	vec2 yz = f3In.yz;
#line 39 "/app/tests/test_swizzling.py"
	vec3 f3;
#line 40 "/app/tests/test_swizzling.py"
	f3.z = 1;
#line 41 "/app/tests/test_swizzling.py"
	f3.xy = yz;
#line 43 "/app/tests/test_swizzling.py"
	float w = f4In.w;
#line 44 "/app/tests/test_swizzling.py"
	vec4 f4 = f4In.yyzz;
#line 46 "/app/tests/test_swizzling.py"
	f4.xy = yz;
	return x;
}

#line 32 "/app/tests/test_swizzling.py"
void main()
{
}

