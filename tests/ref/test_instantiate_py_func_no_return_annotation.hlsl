[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

// Function with no return annotation - should default to void.
//
#line 129 "/app/tests/test_instantiate.py"
void _py_no_return_annotation(float value)
{
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 131 "/app/tests/test_instantiate.py"
PsOut main()
{
#line 132 "/app/tests/test_instantiate.py"
	_py_no_return_annotation(g_f4A.x);
#line 134 "/app/tests/test_instantiate.py"
	PsOut result;
#line 135 "/app/tests/test_instantiate.py"
	result.color = g_f4B;
	return result;
}

