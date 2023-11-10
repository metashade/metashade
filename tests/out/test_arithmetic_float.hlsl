float2 test_arithmetic()
{
	float fD = -1;
	float2 f2A = 0.xx;
	float2 f2B = float2(1, 2);
	float2 f2C = (f2A + f2B);
	f2C = (f2C + f2B);
	f2C = (f2A - f2B);
	f2C = (f2C - f2B);
	f2C = (f2A * f2B);
	f2C = (f2C * f2B);
	f2C = (f2A / f2B);
	f2C = (f2C / f2B);
	f2C = (f2A * fD);
	f2C = (f2C * fD);
	f2C = (f2A / fD);
	f2C = (f2C / fD);
	return f2C;
}

