#version 450
int sum_up_to(int n)
{
	int total = 0;
	for (int i = 0; i < n; ++i)
	{
		total += i;
	}
	return total;
}

void main()
{
}

