#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec3 g_f3A;
	vec3 g_f3B;
};

struct ExternStruct { vec3 response; vec3 throughput; };

ExternStruct computeStruct(vec3 a, vec3 b)
{
	ExternStruct result;
	result.response = a;
	result.throughput = b;
	return result;
}

layout(location = 0) out vec4 out_Color;
void main()
{
	ExternStruct s = computeStruct(g_f3A, g_f3B);
	vec4 final_color = vec4(s.response + s.throughput, 1.0);
	out_Color = final_color;
}

