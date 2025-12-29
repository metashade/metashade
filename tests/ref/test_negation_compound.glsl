#version 450
float test_negation_compound()
{
	float a = 1.0;
	float b = 2.0;
	float sum_ab = a + b;
	float r1 = -sum_ab;
	float r2 = -(a + b);
	float neg_sum = -sum_ab;
	float r3 = neg_sum + a;
	float r4 = neg_sum * b;
	float r5 = -(-a);
	float r6 = -(-sum_ab);
	return r1;
}

void main()
{
}

