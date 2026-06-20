#version 450
vec4 _py_func(bool flag, vec4 a, vec4 b)
{
	if (flag)
	{
		return a;
	}
	return b;
}

void main()
{
}

