#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec3 g_f3A;
	vec3 g_f3B;
};

struct BSDF
{
	vec3 response;
	vec3 throughput;
};

BSDF testConstructorInit(vec3 a, vec3 b)
{
	// Default construction uses member defaults
	BSDF result = BSDF(vec3(0), vec3(1));
	// Explicit kwargs override defaults
	BSDF custom = BSDF(vec3(0.5), vec3(0.25));
	// With lvalue members
	BSDF from_args = BSDF(a, b);
	// Overwrite a member after construction
	result.response = from_args.response;
	return result;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	BSDF bsdf = testConstructorInit(g_f3A, g_f3B);
	vec4 final = vec4(bsdf.response + bsdf.throughput, 1.0);
	out_f4Color = final;
}

