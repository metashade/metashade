#version 450
int nested_sum(int rows, int cols)
{
	int total = 0;
	for (int r = 0; r < rows; r += 1)
	{
		for (int c = 0; c < cols; c += 1)
		{
			total += (r * cols) + c;
		}
	}
	return total;
}

void main()
{
}

