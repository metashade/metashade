int2 test_arithmetic()
{
	int fD = -1;
	int2 f2A = 0.xx;
	int2 f2B = int2(1, 2);
	int2 f2C = f2A + f2B;
	f2C = f2C + f2B;
	f2C = f2A - f2B;
	f2C = f2C - f2B;
	f2C = f2A * f2B;
	f2C = f2C * f2B;
	f2C = f2A / f2B;
	f2C = f2C / f2B;
	f2C = f2A * fD;
	f2C = f2C * fD;
	f2C = f2A / fD;
	f2C = f2C / fD;
	return f2C;
}

void main()
{
}

