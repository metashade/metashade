#version 450
vec4 sum_array()
{
	vec4 arr[4];
	vec4 total = vec4(0.0);
	for (int i = 0; i < 4; i += 1)
	{
		total += arr[i];
	}
	return total;
}

void main()
{
}

