#version 450
vec3 test(vec3 tint, vec3 v, vec3 p, vec3 q, float s)
{
	vec3 magenta = vec3(1.0, 0.0, 1.0);
	vec3 offset = p - q;
	float d = dot(v, offset);
	float red = magenta.r + p.x;
	return (tint * magenta) * (s + (d * red));
}

void main()
{
}

