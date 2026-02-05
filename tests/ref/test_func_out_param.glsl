#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

#line 211 "/app/tests/test_functions.py"
void addOutParam(vec4 a, vec4 b, out vec4 c)
{
#line 214 "/app/tests/test_functions.py"
	c = a + b;
	return;
}

layout(location = 0) out vec4 out_f4Color;
#line 217 "/app/tests/test_functions.py"
void main()
{
#line 218 "/app/tests/test_functions.py"
	vec4 result_color;
#line 219 "/app/tests/test_functions.py"
	addOutParam(g_f4A, g_f4B, result_color);
#line 228 "/app/tests/test_functions.py"
	out_f4Color = result_color;
}

