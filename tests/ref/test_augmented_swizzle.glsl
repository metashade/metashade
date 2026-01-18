#version 450
vec2 test_swizzle(vec2 v, float f)
{
	v.x += f;
	v.x = v.x;
	v.xy += v;
	v.xy = v.xy;
	return v;
}

void main()
{
}

