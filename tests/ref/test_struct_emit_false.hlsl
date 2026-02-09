struct ExternStruct { float3 response; float3 throughput; };

void useStruct(ExternStruct s)
{
	float3 result = s.response + s.throughput;
	return;
}

void main()
{
}

