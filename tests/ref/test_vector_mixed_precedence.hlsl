#line 154 "/app/tests/test_precedence.py"
float3 test_vector_precedence()
{
#line 155 "/app/tests/test_precedence.py"
	float3 v1 = float3(1.0, 2.0, 3.0);
#line 156 "/app/tests/test_precedence.py"
	float3 v2 = float3(4.0, 5.0, 6.0);
#line 157 "/app/tests/test_precedence.py"
	float s = 2.0;
#line 160 "/app/tests/test_precedence.py"
	float3 r1 = (v1 + v2) * s;
#line 163 "/app/tests/test_precedence.py"
	float3 r2 = (v1 * s) + v2;
#line 166 "/app/tests/test_precedence.py"
	float3 r3 = -v1;
#line 169 "/app/tests/test_precedence.py"
	float3 r4 = -(v1 + v2);
	return r1;
}

#line 153 "/app/tests/test_precedence.py"
void main()
{
}

