#version 450
#line 99 "/app/tests/test_precedence.py"
float test_negation_compound()
{
#line 100 "/app/tests/test_precedence.py"
	float a = 1.0;
#line 101 "/app/tests/test_precedence.py"
	float b = 2.0;
#line 104 "/app/tests/test_precedence.py"
	float sum_ab = a + b;
#line 105 "/app/tests/test_precedence.py"
	float r1 = -sum_ab;
#line 109 "/app/tests/test_precedence.py"
	float r2 = -(a + b);
#line 112 "/app/tests/test_precedence.py"
	float neg_sum = -sum_ab;
#line 113 "/app/tests/test_precedence.py"
	float r3 = neg_sum + a;
#line 114 "/app/tests/test_precedence.py"
	float r4 = neg_sum * b;
#line 117 "/app/tests/test_precedence.py"
	float r5 = -(-a);
#line 120 "/app/tests/test_precedence.py"
	float r6 = -(-sum_ab);
	return r1;
}

#line 98 "/app/tests/test_precedence.py"
void main()
{
}

