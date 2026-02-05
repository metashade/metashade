#line 42 "/app/tests/test_precedence.py"
float test_mixed_precedence()
{
#line 43 "/app/tests/test_precedence.py"
	float a = 1.0;
#line 44 "/app/tests/test_precedence.py"
	float b = 2.0;
#line 45 "/app/tests/test_precedence.py"
	float c = 3.0;
#line 48 "/app/tests/test_precedence.py"
	float r1 = (a + b) * c;
#line 51 "/app/tests/test_precedence.py"
	float r2 = a * (b + c);
#line 54 "/app/tests/test_precedence.py"
	float r3 = (a * b) + c;
#line 57 "/app/tests/test_precedence.py"
	float r4 = a + (b * c);
#line 60 "/app/tests/test_precedence.py"
	float r5 = (a + b) + c;
#line 65 "/app/tests/test_precedence.py"
	float r6 = a + (b * c);
	return r1;
}

#line 41 "/app/tests/test_precedence.py"
void main()
{
}

