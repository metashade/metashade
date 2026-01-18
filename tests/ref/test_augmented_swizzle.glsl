#version 450
vec2 test_swizzle(vec2 v, float f)
{
	v.x += f;
	v.xy += v;
	return v;
}

void main()
{
}

