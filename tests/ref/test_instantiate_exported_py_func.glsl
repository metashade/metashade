#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec4 g_f4C;
};

vec4 py_add(vec4 a, vec4 b)
{
	vec4 c = a + b;
	return c;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 c = py_add(g_f4A, g_f4B);
	out_f4Color = c;
}

