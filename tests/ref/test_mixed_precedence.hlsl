float test_mixed_precedence()
{
	float a = 1.0;
	float b = 2.0;
	float c = 3.0;
	float r1 = (a + b) * c;
	float r2 = a * (b + c);
	float r3 = (a * b) + c;
	float r4 = a + (b * c);
	float r5 = (a + b) + c;
	float r6 = a + (b * c);
	return r1;
}

void main()
{
}

