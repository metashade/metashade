#version 450
#line 77 "/app/tests/test_precedence.py"
float test_negation_simple()
{
#line 78 "/app/tests/test_precedence.py"
	float a = 1.0;
#line 81 "/app/tests/test_precedence.py"
	float r1 = -a;
#line 84 "/app/tests/test_precedence.py"
	float r2 = -a + a;
#line 87 "/app/tests/test_precedence.py"
	float r3 = a + -a;
	return r1;
}

#line 76 "/app/tests/test_precedence.py"
void main()
{
}

