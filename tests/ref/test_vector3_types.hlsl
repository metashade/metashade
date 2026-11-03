float3 test(float3 tint, float3 v, float3 p, float3 q, float s)
{
	float3 magenta = float3(1.0, 0.0, 1.0);
	float3 offset = p - q;
	float d = dot(v, offset);
	float red = magenta.r + p.x;
	return (tint * magenta) * (s + (d * red));
}

void main()
{
}

