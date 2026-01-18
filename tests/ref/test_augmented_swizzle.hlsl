float2 test_swizzle(float2 v, float f)
{
	v.x += f;
	v.xy += v;
	return v;
}

void main()
{
}

