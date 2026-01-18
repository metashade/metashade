#version 450
#line 53 "/app/tests/test_swizzling.py"
float expr_swizzle(vec4 v1, vec4 v2)
{
#line 57 "/app/tests/test_swizzling.py"
	float res1 = (v1 + v2).x;
#line 60 "/app/tests/test_swizzling.py"
	float res2 = ((v1 * v2) + v1).w;
	return res1 + res2;
}

#line 52 "/app/tests/test_swizzling.py"
void main()
{
}

