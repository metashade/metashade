struct Pair
{
	float x;
	float y;
};

void fill(out Pair dst)
{
	dst.x = 1.0;
	dst.y = 2.0;
}

void swap(inout Pair pair)
{
	float tmp = pair.x;
	pair.x = pair.y;
	pair.y = tmp;
}

void main()
{
}

