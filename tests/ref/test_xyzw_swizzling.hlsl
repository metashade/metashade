float xyzw_swizzle(float3 f3In, float4 f4In)
{
	float x = f3In.x;
	float2 yz = f3In.yz;
	float3 f3;
	f3.z = 1;
	f3.xy = yz;
	float w = f4In.w;
	float4 f4 = f4In.yyzz;
	f4.xy = yz;
	return x;
}

void main()
{
}

