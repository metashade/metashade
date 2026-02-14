#version 450
struct ExternStruct { vec3 response; vec3 throughput; };

void useStruct(ExternStruct s)
{
	vec3 result = s.response + s.throughput;
	return;
}

void main()
{
}

