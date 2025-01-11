#version 450
float xyzw_swizzle(vec3 f3In, vec4 f4In)
{
	float x = f3In.x;
	vec2 yz = f3In.yz;
	vec3 f3;
	f3.z = 1;
	f3.xy = yz;
	float w = f4In.w;
	vec4 f4 = f4In.yyzz;
	f4.xy = yz;
	return x;
}

void main()
{
}

