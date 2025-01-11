float vector_init()
{
	float f = 1;
	float2 f2 = f.xx;
	f2 = 2.xx;
	f2 = 0.xx;
	f2 = float2(0, 1);
	f2 = float2(3, 4);
	f2 = float2(5, 6);
	f2 = float2(f, 7);
	f2 = float2(8, 9);
	float3 f3 = f.xxx;
	f3 = 0.xxx;
	f3 = 2.xxx;
	f3 = float3(0, 1, 2);
	f3 = float3(f, 3, 4.1);
	float3 p3 = f.xxx;
	p3 = 2.xxx;
	p3 = 0.xxx;
	p3 = float3(0, 1, 0.5);
	p3 = float3(0.1, f, 3);
	float4 v4 = f.xxxx;
	v4 = 2.xxxx;
	v4 = 0.xxxx;
	v4 = float4(0, 1, 0.5, 1.0);
	v4 = float4(0.1, f, 3, 1.0);
	float3 rgb = f.xxx;
	rgb = 2.xxx;
	rgb = 0.xxx;
	rgb = float3(0, 1, 0.5);
	rgb = float3(0.1, f, 3);
	float4 rgba = f.xxxx;
	rgba = 2.xxxx;
	rgba = 0.xxxx;
	rgba = float4(0, 1, 0.5, 1.0);
	rgba = float4(0.1, f, 3, 1.0);
	rgba = float4(rgb, 0.0);
	return f;
}

void main()
{
}

