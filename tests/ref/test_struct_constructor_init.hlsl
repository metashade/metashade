[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float3 g_f3A;
	float3 g_f3B;
};

struct BSDF
{
	float3 response;
	float3 throughput;
};

BSDF testConstructorInit(float3 a, float3 b)
{
	// Constructor-style initialization with scalar broadcast
	BSDF result = {0.xxx, 1.xxx};
	// With lvalue members
	BSDF from_args = {a, b};
	// Overwrite a member after construction
	result.response = from_args.response;
	return result;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	BSDF bsdf = testConstructorInit(g_f3A, g_f3B);
	float4 final = float4(bsdf.response + bsdf.throughput, 1.0);
	PsOut out_struct;
	out_struct.color = final;
	return out_struct;
}

