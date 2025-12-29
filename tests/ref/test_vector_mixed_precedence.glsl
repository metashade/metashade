#version 450
vec3 test_vector_precedence()
{
	vec3 v1 = vec3(1.0, 2.0, 3.0);
	vec3 v2 = vec3(4.0, 5.0, 6.0);
	float s = 2.0;
	vec3 r1 = (v1 + v2) * s;
	vec3 r2 = (v1 * s) + v2;
	vec3 r3 = -v1;
	vec3 r4 = -(v1 + v2);
	return r1;
}

void main()
{
}

