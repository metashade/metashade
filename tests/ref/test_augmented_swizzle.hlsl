float2 test_swizzle(float2 v, float f)
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

