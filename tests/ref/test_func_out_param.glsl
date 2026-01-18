#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

void addOutParam(vec4 a, vec4 b, out vec4 c)
{
	c = a + b;
	return;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 result_color;
	addOutParam(g_f4A, g_f4B, result_color);
	out_f4Color = result_color;
}

