float3 test_vector_precedence()
{
	float3 v1 = float3(1.0, 2.0, 3.0);
	float3 v2 = float3(4.0, 5.0, 6.0);
	float s = 2.0;
	float3 r1 = (v1 + v2) * s;
	float3 r2 = (v1 * s) + v2;
	float3 r3 = -v1;
	float3 r4 = -(v1 + v2);
	return r1;
}

void main()
{
}

