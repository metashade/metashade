float test()
{
	float4 f4A = 1.0.xxxx;
	float4 f4B = 0.0.xxxx - f4A;
	float3 f3A = 0.0.xxx;
	float3 f3B = f3A + 1.0.xxx;
	float2 f2A = 0.6578467.xx;
	float2 f2B = 0.4235.xx * f2A;
	float fA = 1.0;
	float fB = 2.0 + fA;
	return ((f4B.w + f3B.z) + f2B.y) + fB;
}

void main()
{
}

