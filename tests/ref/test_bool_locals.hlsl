float select(float a, float b)
{
	bool enabled = true;
	bool greater = a > b;
	if (enabled)
	{
		if (greater)
		{
			return a;
		}
	}
	return b;
}

void main()
{
}

