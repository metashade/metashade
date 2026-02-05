#line 9 "/app/tests/test_augmented_swizzle.py"
float2 test_swizzle(float2 v, float f)
{
#line 13 "/app/tests/test_augmented_swizzle.py"
	v.x += f;
#line 18 "/app/tests/test_augmented_swizzle.py"
	v.xy += v;
	return v;
}

#line 8 "/app/tests/test_augmented_swizzle.py"
void main()
{
}

