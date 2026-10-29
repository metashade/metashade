#version 450
float _py_func(bool flag, float a, float b)
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

