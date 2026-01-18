#version 450
float rgba_swizzle(vec3 rgb, vec4 rgba)
{
	float r = rgb.r;
	float g = rgba.g;
	rgba.rb = rgba.rg;
	return r + g;
}

void main()
{
}

