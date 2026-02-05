[[vk::binding(0, 0)]]
cbuffer cb0 : register(b0)
{
	float4 g_f4Color0;
};

[[vk::binding(1, 0)]]
cbuffer cb1 : register(b1)
{
	float4 g_f4Color1;
};

[[vk::binding(0, 1)]]
cbuffer cb2 : register(b2)
{
	float4 g_f4Color2;
};

[[vk::binding(1, 1)]]
cbuffer cb3 : register(b3)
{
	float4 g_f4Color3;
};

#line 96 "/app/tests/test_uniforms.py"
void main()
{
}

