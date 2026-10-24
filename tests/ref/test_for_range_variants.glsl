#version 450
int range_variants(int n)
{
	int total = 0;
	for (int i = 0; i < 4; i += 1)
	{
		total += i;
	}
	for (int i = 1; i < (n + 1); i += 1)
	{
		total += i;
	}
	for (int i = 0; i < 8; i += 2)
	{
		total += i;
	}
	for (int i = 5; i > 0; i -= 1)
	{
		total += i;
	}
	for (int i = 10; i > 0; i -= 2)
	{
		total += i;
	}
	return total;
}

void main()
{
}

