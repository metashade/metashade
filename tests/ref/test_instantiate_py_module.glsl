#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec4 g_f4C;
};

#line 94 "/app/tests/test_instantiate.py"
vec4 py_add(vec4 a, vec4 b)
{
#line 19 "/app/tests/_exports.py"
	vec4 c = a + b;
	return c;
}

#line 94 "/app/tests/test_instantiate.py"
vec4 py_mul(vec4 a, vec4 b)
{
#line 24 "/app/tests/_exports.py"
	vec4 c = a * b;
	return c;
}

#line 94 "/app/tests/test_instantiate.py"
vec4 py_madd(vec4 a, vec4 b, vec4 c)
{
#line 29 "/app/tests/_exports.py"
	vec4 d = py_add(a, b);
#line 30 "/app/tests/_exports.py"
	vec4 e = py_mul(d, c);
	return e;
}

layout(location = 0) out vec4 out_f4Color;
#line 96 "/app/tests/test_instantiate.py"
void main()
{
#line 97 "/app/tests/test_instantiate.py"
	vec4 c = py_madd(g_f4A, g_f4B, g_f4C);
#line 106 "/app/tests/test_instantiate.py"
	out_f4Color = c;
}

