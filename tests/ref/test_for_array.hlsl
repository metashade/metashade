float4 sum_array()
{
	float4 arr[4];
	float4 total = 0.0.xxxx;
	for (int i = 0; i < 4; i += 1)
	{
		total += arr[i];
	}
	return total;
}

void main()
{
}

