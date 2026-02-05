#version 450
#line 41 "/app/tests/test_out_params.py"
void func_with_inout(inout float inout_val)
{
#line 24 "/app/tests/test_out_params.py"
	inout_val = inout_val + 1.0;
}

#line 43 "/app/tests/test_out_params.py"
void main()
{
#line 44 "/app/tests/test_out_params.py"
	float val = 1.0;
#line 45 "/app/tests/test_out_params.py"
	func_with_inout(val);
}

