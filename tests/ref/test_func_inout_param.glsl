#version 450
layout (set = 0, binding = 0) uniform cb
{
	vec4 g_f4A;
	vec4 g_f4B;
	vec3 g_f3C;
};

#line 237 "/app/tests/test_functions.py"
void modifyInOut(inout vec4 value)
{
#line 240 "/app/tests/test_functions.py"
	value = value + value;
	return;
}

layout(location = 0) out vec4 out_f4Color;
#line 243 "/app/tests/test_functions.py"
void main()
{
#line 244 "/app/tests/test_functions.py"
	vec4 test_value = g_f4A;
#line 245 "/app/tests/test_functions.py"
	modifyInOut(test_value);
#line 252 "/app/tests/test_functions.py"
	out_f4Color = test_value;
}

