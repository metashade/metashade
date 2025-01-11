#version 450
float vector_init()
{
	float f = 1;
	vec2 f2 = vec2(f);
	f2 = vec2(2);
	f2 = vec2(0);
	f2 = vec2(0, 1);
	f2 = vec2(3, 4);
	f2 = vec2(5, 6);
	f2 = vec2(f, 7);
	f2 = vec2(8, 9);
	vec3 f3 = vec3(f);
	f3 = vec3(0);
	f3 = vec3(2);
	f3 = vec3(0, 1, 2);
	f3 = vec3(f, 3, 4.1);
	vec3 p3 = vec3(f);
	p3 = vec3(2);
	p3 = vec3(0);
	p3 = vec3(0, 1, 0.5);
	p3 = vec3(0.1, f, 3);
	vec4 v4 = vec4(f);
	v4 = vec4(2);
	v4 = vec4(0);
	v4 = vec4(0, 1, 0.5, 1.0);
	v4 = vec4(0.1, f, 3, 1.0);
	vec3 rgb = vec3(f);
	rgb = vec3(2);
	rgb = vec3(0);
	rgb = vec3(0, 1, 0.5);
	rgb = vec3(0.1, f, 3);
	vec4 rgba = vec4(f);
	rgba = vec4(2);
	rgba = vec4(0);
	rgba = vec4(0, 1, 0.5, 1.0);
	rgba = vec4(0.1, f, 3, 1.0);
	rgba = vec4(rgb, 0.0);
	return f;
}

void main()
{
}

