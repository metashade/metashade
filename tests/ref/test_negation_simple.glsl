#version 450
float test_negation_simple()
{
	float a = 1.0;
	float r1 = -a;
	float r2 = -a + a;
	float r3 = a + -a;
	return r1;
}

void main()
{
}

