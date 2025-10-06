#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

void modifyInOut(inout vec4 value)
{
	value = (value + value);
	return;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	vec4 test_value = g_f4A;
	modifyInOut(test_value);
	out_f4Color = test_value;
}

