#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

vec4 externalAdd(vec4 a, vec4 b) { return a + b; }

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 c = externalAdd(g_f4A, g_f4B);
	out_f4Color = c;
}

