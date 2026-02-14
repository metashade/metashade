#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec3 g_f3A;
	vec3 g_f3B;
};

// The struct defined in the target language
struct BSDF { vec3 response; vec3 throughput; };

BSDF getBsdf(vec3 r, vec3 t)
{
	// Now, use the struct
	BSDF b;
	b.response = r;
	b.throughput = t;
	return b;
}

layout(location = 0) out vec4 out_f4Color;
void main()
{
	BSDF bsdf = getBsdf(g_f3A, g_f3B);
	vec4 final = vec4(bsdf.response * bsdf.throughput, 1.0);
	out_f4Color = final;
}

