// Procedural randomized cell colors with sinusoidal UV distortion.
//
float3 noisy_squares2d(float2 texcoord, float scale)
{
	float2 uv = texcoord * scale;
	float2 warp = float2(sin(uv.y * scale), sin(uv.x * scale));
	uv += warp / scale;
	float seed = floor(uv.x) + (floor(uv.y) * scale);
	float red = sin(seed * 12.9898) * 43758.5453;
	float green = sin(seed * 78.233) * 23421.631;
	float blue = sin(seed * 39.346) * 12741.371;
	return float3(red - floor(red), green - floor(green), blue - floor(blue));
}

void main()
{
}

