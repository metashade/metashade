#version 450
layout (set = 0, binding = 0) uniform cb
{
	bool g_flag;
	vec4 g_f4A;
	vec4 g_f4B;
};

layout(location = 0) out vec4 out_color;
void main()
{
	if (g_flag)
	{
		out_color = g_f4A;
	}
	else
	{
		out_color = g_f4B;
	}
}

