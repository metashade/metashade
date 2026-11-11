// Procedural randomized cell colors with sinusoidal UV distortion.
//
vec3 noisy_squares2d(vec2 texcoord, float scale)
{
	vec2 uv = texcoord * scale;
	vec2 warp = vec2(sin(uv.y * scale), sin(uv.x * scale));
	uv += warp / scale;
	float seed = floor(uv.x) + (floor(uv.y) * scale);
	float red = sin(seed * 12.9898) * 43758.5453;
	float green = sin(seed * 78.233) * 23421.631;
	float blue = sin(seed * 39.346) * 12741.371;
	return vec3(red - floor(red), green - floor(green), blue - floor(blue));
}

void mx_noisy_squares2d_color3(vec2 texcoord, float scale, out vec3 out_)
{
	out_ = noisy_squares2d(texcoord, scale);
}

