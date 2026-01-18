float expr_swizzle(float4 v1, float4 v2)
{
	float res1 = (v1 + v2).x;
	float res2 = ((v1 * v2) + v1).w;
	return res1 + res2;
}

void main()
{
}

