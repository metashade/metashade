#version 450
float expr_swizzle(vec4 v1, vec4 v2)
{
	float res1 = (v1 + v2).x;
	float res2 = ((v1 * v2) + v1).w;
	return res1 + res2;
}

void main()
{
}

