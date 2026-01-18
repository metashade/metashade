#line 24 "/app/tests/test_arithmetic.py"
float2 test_arithmetic()
{
#line 27 "/app/tests/test_arithmetic.py"
	float fD = -1;
#line 29 "/app/tests/test_arithmetic.py"
	float2 f2A = 0.xx;
#line 30 "/app/tests/test_arithmetic.py"
	float2 f2B = float2(1, 2);
#line 32 "/app/tests/test_arithmetic.py"
	float2 f2C = f2A + f2B;
#line 33 "/app/tests/test_arithmetic.py"
	f2C += f2B;
#line 35 "/app/tests/test_arithmetic.py"
	f2C = f2A - f2B;
#line 36 "/app/tests/test_arithmetic.py"
	f2C -= f2B;
#line 38 "/app/tests/test_arithmetic.py"
	f2C = f2A * f2B;
#line 39 "/app/tests/test_arithmetic.py"
	f2C *= f2B;
#line 41 "/app/tests/test_arithmetic.py"
	f2C = f2A / f2B;
#line 42 "/app/tests/test_arithmetic.py"
	f2C /= f2B;
#line 44 "/app/tests/test_arithmetic.py"
	f2C = f2A * fD;
#line 45 "/app/tests/test_arithmetic.py"
	f2C *= fD;
#line 47 "/app/tests/test_arithmetic.py"
	f2C = f2A / fD;
#line 48 "/app/tests/test_arithmetic.py"
	f2C /= fD;
	return f2C;
}

#line 23 "/app/tests/test_arithmetic.py"
void main()
{
}

