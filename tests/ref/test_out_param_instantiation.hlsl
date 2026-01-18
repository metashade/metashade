#line 31 "/app/tests/test_out_params.py"
void func_with_out(out float out_val)
{
#line 20 "/app/tests/test_out_params.py"
	out_val = 1.0;
}

#line 33 "/app/tests/test_out_params.py"
void main()
{
#line 34 "/app/tests/test_out_params.py"
	float val = 0.0;
#line 35 "/app/tests/test_out_params.py"
	func_with_out(val);
}

