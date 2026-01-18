#version 450
float test()
{
	vec4 f4A = vec4(1.0);
	vec4 f4B = vec4(0.0) - f4A;
	vec3 f3A = vec3(0.0);
	vec3 f3B = f3A + vec3(1.0);
	vec2 f2A = vec2(0.6578467);
	vec2 f2B = vec2(0.4235) * f2A;
	float fA = 1.0;
	float fB = 2.0 + fA;
	return ((f4B.w + f3B.z) + f2B.y) + fB;
}

void main()
{
}

