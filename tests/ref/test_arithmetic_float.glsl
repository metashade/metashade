#version 450
vec2 test_arithmetic()
{
	float fD = -1;
	vec2 f2A = vec2(0);
	vec2 f2B = vec2(1, 2);
	vec2 f2C = f2A + f2B;
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

