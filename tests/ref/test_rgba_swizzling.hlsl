#line 22 "/app/tests/test_swizzling.py"
float rgba_swizzle(float3 rgb, float4 rgba)
{
#line 25 "/app/tests/test_swizzling.py"
	float r = rgb.r;
#line 26 "/app/tests/test_swizzling.py"
	float g = rgba.g;
#line 27 "/app/tests/test_swizzling.py"
	rgba.rb = rgba.rg;
	return r + g;
}

#line 21 "/app/tests/test_swizzling.py"
void main()
{
}

