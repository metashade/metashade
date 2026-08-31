#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec3 g_f3A;
	vec3 g_f3B;
};

// The struct defined in the target language
struct BSDF { vec3 response; vec3 throughput; };

BSDF testConstructorInit(vec3 a, vec3 b)
{
	// Constructor-style initialization
	BSDF result = BSDF(vec3(0.0, 0.0, 0.0), vec3(1.0, 1.0, 1.0));
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

