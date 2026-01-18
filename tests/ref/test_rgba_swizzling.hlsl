float rgba_swizzle(float3 rgb, float4 rgba)
{
	float r = rgb.r;
	float g = rgba.g;
	rgba.rb = rgba.rg;
	return r + g;
}

void main()
{
}

