#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec4 g_f4C;
};

#line 74 "/app/tests/test_instantiate.py"
vec4 py_add(vec4 a, vec4 b)
{
#line 19 "/app/tests/_exports.py"
	vec4 c = a + b;
	return c;
}

layout(location = 0) out vec4 out_f4Color;
#line 76 "/app/tests/test_instantiate.py"
void main()
{
#line 77 "/app/tests/test_instantiate.py"
	vec4 c = py_add(g_f4A, g_f4B);
#line 84 "/app/tests/test_instantiate.py"
	out_f4Color = c;
}

