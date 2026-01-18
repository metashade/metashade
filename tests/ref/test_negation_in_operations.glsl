#version 450
float test_negation_in_ops()
{
	float a = 1.0;
	float b = 2.0;
	float r1 = -a + b;
	float r2 = -a * b;
	float r3 = a + -b;
	float r4 = a * -b;
	float c = 3.0;
	float r5 = (-a + b) + c;
	return r1;
}

void main()
{
}

