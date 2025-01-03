#version 450
layout (set = 0, binding = 0) uniform cb0
{
	vec4 g_f4Color0;
};

layout (set = 0, binding = 0) uniform cb1
{
	vec4 g_f4Color1;
};

layout (set = 1, binding = 1) uniform cb2
{
	vec4 g_f4Color2;
};

layout (set = 1, binding = 1) uniform cb3
{
	vec4 g_f4Color3;
};

layout(location = 0) out vec4 out_f4Color;
void main()
{
	out_f4Color = g_f4Color0;
}
