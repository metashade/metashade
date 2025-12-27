#version 450
void func_with_inout(inout float inout_val)
{
	inout_val = (inout_val + 1.0);
}

void main()
{
	float val = 1.0;
	func_with_inout(val);
}
