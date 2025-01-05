#version 450
layout (vk_set = 0, vk_binding = 0) uniform cb0
{
	vec4 g_f4Color;
};

layout(location = 0) out vec4 out_f4Color;
void main()
{
	out_f4Color = g_f4Color;
}

