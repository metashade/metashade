#version 450
layout (set = 0, binding = 0) uniform cb
{
	float g_x;
	vec4 g_f4A;
	vec4 g_f4B;
};

layout(location = 0) out vec4 out_color;
void main()
{
	if (g_x > 0.0)
	{
		out_color = g_f4A;
	}
	else
	{
		out_color = g_f4B;
	}
}

