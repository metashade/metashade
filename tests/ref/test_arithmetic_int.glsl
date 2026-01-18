#version 450
ivec2 test_arithmetic()
{
	int fD = -1;
	ivec2 f2A = ivec2(0);
	ivec2 f2B = ivec2(1, 2);
	ivec2 f2C = f2A + f2B;
	f2C += f2B;
	f2C = f2A - f2B;
	f2C -= f2B;
	f2C = f2A * f2B;
	f2C *= f2B;
	f2C = f2A / f2B;
	f2C /= f2B;
	f2C = f2A * fD;
	f2C *= fD;
	f2C = f2A / fD;
	f2C /= fD;
	return f2C;
}

void main()
{
}

