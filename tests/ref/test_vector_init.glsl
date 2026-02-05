#version 450
#line 21 "/app/tests/test_vector_init.py"
float vector_init()
{
#line 22 "/app/tests/test_vector_init.py"
	float f = 1;
#line 24 "/app/tests/test_vector_init.py"
	vec2 f2 = vec2(f);
#line 25 "/app/tests/test_vector_init.py"
	f2 = vec2(2);
#line 26 "/app/tests/test_vector_init.py"
	f2 = vec2(0);
#line 27 "/app/tests/test_vector_init.py"
	f2 = vec2(0, 1);
#line 28 "/app/tests/test_vector_init.py"
	f2 = vec2(3, 4);
#line 29 "/app/tests/test_vector_init.py"
	f2 = vec2(5, 6);
#line 30 "/app/tests/test_vector_init.py"
	f2 = vec2(f, 7);
#line 31 "/app/tests/test_vector_init.py"
	f2 = vec2(8, 9);
#line 33 "/app/tests/test_vector_init.py"
	vec3 f3 = vec3(f);
#line 34 "/app/tests/test_vector_init.py"
	f3 = vec3(0);
#line 35 "/app/tests/test_vector_init.py"
	f3 = vec3(2);
#line 36 "/app/tests/test_vector_init.py"
	f3 = vec3(0, 1, 2);
#line 37 "/app/tests/test_vector_init.py"
	f3 = vec3(f, 3, 4.1);
#line 39 "/app/tests/test_vector_init.py"
	vec3 p3 = vec3(f);
#line 40 "/app/tests/test_vector_init.py"
	p3 = vec3(2);
#line 41 "/app/tests/test_vector_init.py"
	p3 = vec3(0);
#line 42 "/app/tests/test_vector_init.py"
	p3 = vec3(0, 1, 0.5);
#line 43 "/app/tests/test_vector_init.py"
	p3 = vec3(0.1, f, 3);
#line 45 "/app/tests/test_vector_init.py"
	vec4 v4 = vec4(f);
#line 46 "/app/tests/test_vector_init.py"
	v4 = vec4(2);
#line 47 "/app/tests/test_vector_init.py"
	v4 = vec4(0);
#line 48 "/app/tests/test_vector_init.py"
	v4 = vec4(0, 1, 0.5, 1.0);
#line 49 "/app/tests/test_vector_init.py"
	v4 = vec4(0.1, f, 3, 1.0);
#line 51 "/app/tests/test_vector_init.py"
	vec3 rgb = vec3(f);
#line 52 "/app/tests/test_vector_init.py"
	rgb = vec3(2);
#line 53 "/app/tests/test_vector_init.py"
	rgb = vec3(0);
#line 54 "/app/tests/test_vector_init.py"
	rgb = vec3(0, 1, 0.5);
#line 55 "/app/tests/test_vector_init.py"
	rgb = vec3(0.1, f, 3);
#line 57 "/app/tests/test_vector_init.py"
	vec4 rgba = vec4(f);
#line 58 "/app/tests/test_vector_init.py"
	rgba = vec4(2);
#line 59 "/app/tests/test_vector_init.py"
	rgba = vec4(0);
#line 60 "/app/tests/test_vector_init.py"
	rgba = vec4(0, 1, 0.5, 1.0);
#line 61 "/app/tests/test_vector_init.py"
	rgba = vec4(0.1, f, 3, 1.0);
#line 62 "/app/tests/test_vector_init.py"
	rgba = vec4(rgb, 0.0);
	return f;
}

#line 20 "/app/tests/test_vector_init.py"
void main()
{
}

