float4 rgba_rgb_augmented(float4 rgba, float3 rgb)
{
	rgba.rgb += rgb;
	rgba.rgb = rgba.rgb;
	return rgba;
}

void main()
{
}

