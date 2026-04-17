#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

vec4 add_with_default(vec4 a, vec4 b)
{
	vec4 c = a + b;
	return c;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 c = add_with_default(g_f4A, vec4(1.0, 1.0, 1.0, 1.0));
	vec4 c2 = add_with_default(g_f4A, g_f4B);
	out_f4Color = c + c2;
}

