#line 128 "/app/tests/test_precedence.py"
float test_negation_in_ops()
{
#line 129 "/app/tests/test_precedence.py"
	float a = 1.0;
#line 130 "/app/tests/test_precedence.py"
	float b = 2.0;
#line 133 "/app/tests/test_precedence.py"
	float r1 = -a + b;
#line 134 "/app/tests/test_precedence.py"
	float r2 = -a * b;
#line 137 "/app/tests/test_precedence.py"
	float r3 = a + -b;
#line 138 "/app/tests/test_precedence.py"
	float r4 = a * -b;
#line 141 "/app/tests/test_precedence.py"
	float c = 3.0;
#line 142 "/app/tests/test_precedence.py"
	float r5 = (-a + b) + c;
	return r1;
}

#line 127 "/app/tests/test_precedence.py"
void main()
{
}

