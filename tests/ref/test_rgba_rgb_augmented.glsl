#version 450
#line 68 "/app/tests/test_swizzling.py"
vec4 rgba_rgb_augmented(vec4 rgba, vec3 rgb)
{
#line 72 "/app/tests/test_swizzling.py"
	rgba.rgb += rgb;
	return rgba;
}

#line 67 "/app/tests/test_swizzling.py"
void main()
{
}

