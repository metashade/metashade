#version 450
#line 29 "/app/tests/test_functions.py"
vec4 add(vec4 a, vec4 b)
{
	return a + b;
}

layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

layout(location = 0) out vec4 out_f4Color;
#line 55 "/app/tests/test_functions.py"
void main()
{
#line 56 "/app/tests/test_functions.py"
	vec4 c = add(g_f4A, g_f4B);
#line 63 "/app/tests/test_functions.py"
	out_f4Color = c;
}

