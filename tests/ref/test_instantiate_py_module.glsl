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

vec4 py_mul(vec4 a, vec4 b)
{
	vec4 c = a * b;
	return c;
}

vec4 py_madd(vec4 a, vec4 b, vec4 c)
{
	vec4 d = py_add(a, b);
	vec4 e = py_mul(d, c);
	return e;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 c = py_madd(g_f4A, g_f4B, g_f4C);
	out_f4Color = c;
}

