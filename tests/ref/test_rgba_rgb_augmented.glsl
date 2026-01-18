#version 450
vec4 rgba_rgb_augmented(vec4 rgba, vec3 rgb)
{
	rgba.rgb += rgb;
	return rgba;
}

void main()
{
}

