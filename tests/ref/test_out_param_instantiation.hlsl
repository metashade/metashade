void func_with_out(out float out_val)
{
	out_val = 1.0;
}

void main()
{
	float val = 0.0;
	func_with_out(val);
}
