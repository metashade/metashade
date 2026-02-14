[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float3 g_f3A;
	float3 g_f3B;
};

// The struct defined in the target language
struct ExternStruct { float3 response; float3 throughput; };

ExternStruct computeStruct(float3 a, float3 b)
{
	// Now, use the struct
	ExternStruct result;
	result.response = a;
	result.throughput = b;
	return result;
}

struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut main()
{
	ExternStruct s = computeStruct(g_f3A, g_f3B);
	float4 final_color = float4(s.response + s.throughput, 1.0);
	PsOut out_struct;
	out_struct.color = final_color;
	return out_struct;
}

