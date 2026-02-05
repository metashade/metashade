[[vk::binding(0, 0)]]
cbuffer cb : register(b0)
{
	float4 g_f4A;
	float4 g_f4B;
	float4 g_f4C;
};

#line 114 "/app/tests/test_instantiate.py"
void _py_clip(float value)
{
	clip(value);
}

struct PsOut
{
	float4 color : SV_TARGET;
};

#line 116 "/app/tests/test_instantiate.py"
PsOut main()
{
#line 118 "/app/tests/test_instantiate.py"
	_py_clip(g_f4A.x);
#line 120 "/app/tests/test_instantiate.py"
	PsOut result;
#line 121 "/app/tests/test_instantiate.py"
	result.color = g_f4B;
	return result;
}

