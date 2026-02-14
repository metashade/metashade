[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float3 g_f3A;
	float3 g_f3B;
};

// The struct defined in the target language
struct BSDF { float3 response; float3 throughput; };

BSDF getBsdf(float3 r, float3 t)
{
	// Now, use the struct
	BSDF b;
	b.response = r;
	b.throughput = t;
	return b;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	BSDF bsdf = getBsdf(g_f3A, g_f3B);
	float4 final = float4(bsdf.response * bsdf.throughput, 1.0);
	PsOut out_struct;
	out_struct.color = final;
	return out_struct;
}

