#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec4 g_f4C;
};

#line 54 "/app/tests/test_instantiate.py"
vec4 _py_add(vec4 a, vec4 b)
{
#line 18 "/app/tests/test_instantiate.py"
	vec4 c = a + b;
	return c;
}

layout(location = 0) out vec4 out_f4Color;
#line 56 "/app/tests/test_instantiate.py"
void main()
{
#line 57 "/app/tests/test_instantiate.py"
	vec4 c = _py_add(g_f4A, g_f4B);
#line 64 "/app/tests/test_instantiate.py"
	out_f4Color = c;
}

