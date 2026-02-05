cbuffer cb : register(b0)
{
	float g_f;
	float1 g_f1;
	float2 g_f2;
	float3 g_f3;
	float4 g_f4;
	float1x1 g_f1x1;
	float1x2 g_f1x2;
	float1x3 g_f1x3;
	float1x4 g_f1x4;
	float2x1 g_f2x1;
	float2x2 g_f2x2;
	float2x3 g_f2x3;
	float2x4 g_f2x4;
	float3x1 g_f3x1;
	float3x2 g_f3x2;
	float3x3 g_f3x3;
	float3x4 g_f3x4;
	float4x1 g_f4x1;
	float4x2 g_f4x2;
	float4x3 g_f4x3;
	float4x4 g_f4x4;
};

#line 19 "/app/tests/_auto_numeric_intrinsics.py"
float test_EvaluateAttributeCentroid_Float()
{
	return EvaluateAttributeCentroid(g_f);
}

#line 22 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_EvaluateAttributeCentroid_Float1()
{
	return EvaluateAttributeCentroid(g_f1);
}

#line 25 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_EvaluateAttributeCentroid_Float2()
{
	return EvaluateAttributeCentroid(g_f2);
}

#line 28 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_EvaluateAttributeCentroid_Float3()
{
	return EvaluateAttributeCentroid(g_f3);
}

#line 31 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_EvaluateAttributeCentroid_Float4()
{
	return EvaluateAttributeCentroid(g_f4);
}

#line 34 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_EvaluateAttributeCentroid_Float1x1()
{
	return EvaluateAttributeCentroid(g_f1x1);
}

#line 37 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_EvaluateAttributeCentroid_Float1x2()
{
	return EvaluateAttributeCentroid(g_f1x2);
}

#line 40 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_EvaluateAttributeCentroid_Float1x3()
{
	return EvaluateAttributeCentroid(g_f1x3);
}

#line 43 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_EvaluateAttributeCentroid_Float1x4()
{
	return EvaluateAttributeCentroid(g_f1x4);
}

#line 46 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_EvaluateAttributeCentroid_Float2x1()
{
	return EvaluateAttributeCentroid(g_f2x1);
}

#line 49 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_EvaluateAttributeCentroid_Float2x2()
{
	return EvaluateAttributeCentroid(g_f2x2);
}

#line 52 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_EvaluateAttributeCentroid_Float2x3()
{
	return EvaluateAttributeCentroid(g_f2x3);
}

#line 55 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_EvaluateAttributeCentroid_Float2x4()
{
	return EvaluateAttributeCentroid(g_f2x4);
}

#line 58 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_EvaluateAttributeCentroid_Float3x1()
{
	return EvaluateAttributeCentroid(g_f3x1);
}

#line 61 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_EvaluateAttributeCentroid_Float3x2()
{
	return EvaluateAttributeCentroid(g_f3x2);
}

#line 64 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_EvaluateAttributeCentroid_Float3x3()
{
	return EvaluateAttributeCentroid(g_f3x3);
}

#line 67 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_EvaluateAttributeCentroid_Float3x4()
{
	return EvaluateAttributeCentroid(g_f3x4);
}

#line 70 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_EvaluateAttributeCentroid_Float4x1()
{
	return EvaluateAttributeCentroid(g_f4x1);
}

#line 73 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_EvaluateAttributeCentroid_Float4x2()
{
	return EvaluateAttributeCentroid(g_f4x2);
}

#line 76 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_EvaluateAttributeCentroid_Float4x3()
{
	return EvaluateAttributeCentroid(g_f4x3);
}

#line 79 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_EvaluateAttributeCentroid_Float4x4()
{
	return EvaluateAttributeCentroid(g_f4x4);
}

#line 82 "/app/tests/_auto_numeric_intrinsics.py"
float test_QuadReadAcrossDiagonal_Float()
{
	return QuadReadAcrossDiagonal(g_f);
}

#line 85 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_QuadReadAcrossDiagonal_Float1()
{
	return QuadReadAcrossDiagonal(g_f1);
}

#line 88 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_QuadReadAcrossDiagonal_Float2()
{
	return QuadReadAcrossDiagonal(g_f2);
}

#line 91 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_QuadReadAcrossDiagonal_Float3()
{
	return QuadReadAcrossDiagonal(g_f3);
}

#line 94 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_QuadReadAcrossDiagonal_Float4()
{
	return QuadReadAcrossDiagonal(g_f4);
}

#line 97 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_QuadReadAcrossDiagonal_Float1x1()
{
	return QuadReadAcrossDiagonal(g_f1x1);
}

#line 100 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_QuadReadAcrossDiagonal_Float1x2()
{
	return QuadReadAcrossDiagonal(g_f1x2);
}

#line 103 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_QuadReadAcrossDiagonal_Float1x3()
{
	return QuadReadAcrossDiagonal(g_f1x3);
}

#line 106 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_QuadReadAcrossDiagonal_Float1x4()
{
	return QuadReadAcrossDiagonal(g_f1x4);
}

#line 109 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_QuadReadAcrossDiagonal_Float2x1()
{
	return QuadReadAcrossDiagonal(g_f2x1);
}

#line 112 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_QuadReadAcrossDiagonal_Float2x2()
{
	return QuadReadAcrossDiagonal(g_f2x2);
}

#line 115 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_QuadReadAcrossDiagonal_Float2x3()
{
	return QuadReadAcrossDiagonal(g_f2x3);
}

#line 118 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_QuadReadAcrossDiagonal_Float2x4()
{
	return QuadReadAcrossDiagonal(g_f2x4);
}

#line 121 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_QuadReadAcrossDiagonal_Float3x1()
{
	return QuadReadAcrossDiagonal(g_f3x1);
}

#line 124 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_QuadReadAcrossDiagonal_Float3x2()
{
	return QuadReadAcrossDiagonal(g_f3x2);
}

#line 127 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_QuadReadAcrossDiagonal_Float3x3()
{
	return QuadReadAcrossDiagonal(g_f3x3);
}

#line 130 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_QuadReadAcrossDiagonal_Float3x4()
{
	return QuadReadAcrossDiagonal(g_f3x4);
}

#line 133 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_QuadReadAcrossDiagonal_Float4x1()
{
	return QuadReadAcrossDiagonal(g_f4x1);
}

#line 136 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_QuadReadAcrossDiagonal_Float4x2()
{
	return QuadReadAcrossDiagonal(g_f4x2);
}

#line 139 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_QuadReadAcrossDiagonal_Float4x3()
{
	return QuadReadAcrossDiagonal(g_f4x3);
}

#line 142 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_QuadReadAcrossDiagonal_Float4x4()
{
	return QuadReadAcrossDiagonal(g_f4x4);
}

#line 145 "/app/tests/_auto_numeric_intrinsics.py"
float test_QuadReadAcrossX_Float()
{
	return QuadReadAcrossX(g_f);
}

#line 148 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_QuadReadAcrossX_Float1()
{
	return QuadReadAcrossX(g_f1);
}

#line 151 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_QuadReadAcrossX_Float2()
{
	return QuadReadAcrossX(g_f2);
}

#line 154 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_QuadReadAcrossX_Float3()
{
	return QuadReadAcrossX(g_f3);
}

#line 157 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_QuadReadAcrossX_Float4()
{
	return QuadReadAcrossX(g_f4);
}

#line 160 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_QuadReadAcrossX_Float1x1()
{
	return QuadReadAcrossX(g_f1x1);
}

#line 163 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_QuadReadAcrossX_Float1x2()
{
	return QuadReadAcrossX(g_f1x2);
}

#line 166 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_QuadReadAcrossX_Float1x3()
{
	return QuadReadAcrossX(g_f1x3);
}

#line 169 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_QuadReadAcrossX_Float1x4()
{
	return QuadReadAcrossX(g_f1x4);
}

#line 172 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_QuadReadAcrossX_Float2x1()
{
	return QuadReadAcrossX(g_f2x1);
}

#line 175 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_QuadReadAcrossX_Float2x2()
{
	return QuadReadAcrossX(g_f2x2);
}

#line 178 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_QuadReadAcrossX_Float2x3()
{
	return QuadReadAcrossX(g_f2x3);
}

#line 181 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_QuadReadAcrossX_Float2x4()
{
	return QuadReadAcrossX(g_f2x4);
}

#line 184 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_QuadReadAcrossX_Float3x1()
{
	return QuadReadAcrossX(g_f3x1);
}

#line 187 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_QuadReadAcrossX_Float3x2()
{
	return QuadReadAcrossX(g_f3x2);
}

#line 190 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_QuadReadAcrossX_Float3x3()
{
	return QuadReadAcrossX(g_f3x3);
}

#line 193 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_QuadReadAcrossX_Float3x4()
{
	return QuadReadAcrossX(g_f3x4);
}

#line 196 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_QuadReadAcrossX_Float4x1()
{
	return QuadReadAcrossX(g_f4x1);
}

#line 199 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_QuadReadAcrossX_Float4x2()
{
	return QuadReadAcrossX(g_f4x2);
}

#line 202 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_QuadReadAcrossX_Float4x3()
{
	return QuadReadAcrossX(g_f4x3);
}

#line 205 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_QuadReadAcrossX_Float4x4()
{
	return QuadReadAcrossX(g_f4x4);
}

#line 208 "/app/tests/_auto_numeric_intrinsics.py"
float test_QuadReadAcrossY_Float()
{
	return QuadReadAcrossY(g_f);
}

#line 211 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_QuadReadAcrossY_Float1()
{
	return QuadReadAcrossY(g_f1);
}

#line 214 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_QuadReadAcrossY_Float2()
{
	return QuadReadAcrossY(g_f2);
}

#line 217 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_QuadReadAcrossY_Float3()
{
	return QuadReadAcrossY(g_f3);
}

#line 220 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_QuadReadAcrossY_Float4()
{
	return QuadReadAcrossY(g_f4);
}

#line 223 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_QuadReadAcrossY_Float1x1()
{
	return QuadReadAcrossY(g_f1x1);
}

#line 226 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_QuadReadAcrossY_Float1x2()
{
	return QuadReadAcrossY(g_f1x2);
}

#line 229 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_QuadReadAcrossY_Float1x3()
{
	return QuadReadAcrossY(g_f1x3);
}

#line 232 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_QuadReadAcrossY_Float1x4()
{
	return QuadReadAcrossY(g_f1x4);
}

#line 235 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_QuadReadAcrossY_Float2x1()
{
	return QuadReadAcrossY(g_f2x1);
}

#line 238 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_QuadReadAcrossY_Float2x2()
{
	return QuadReadAcrossY(g_f2x2);
}

#line 241 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_QuadReadAcrossY_Float2x3()
{
	return QuadReadAcrossY(g_f2x3);
}

#line 244 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_QuadReadAcrossY_Float2x4()
{
	return QuadReadAcrossY(g_f2x4);
}

#line 247 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_QuadReadAcrossY_Float3x1()
{
	return QuadReadAcrossY(g_f3x1);
}

#line 250 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_QuadReadAcrossY_Float3x2()
{
	return QuadReadAcrossY(g_f3x2);
}

#line 253 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_QuadReadAcrossY_Float3x3()
{
	return QuadReadAcrossY(g_f3x3);
}

#line 256 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_QuadReadAcrossY_Float3x4()
{
	return QuadReadAcrossY(g_f3x4);
}

#line 259 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_QuadReadAcrossY_Float4x1()
{
	return QuadReadAcrossY(g_f4x1);
}

#line 262 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_QuadReadAcrossY_Float4x2()
{
	return QuadReadAcrossY(g_f4x2);
}

#line 265 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_QuadReadAcrossY_Float4x3()
{
	return QuadReadAcrossY(g_f4x3);
}

#line 268 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_QuadReadAcrossY_Float4x4()
{
	return QuadReadAcrossY(g_f4x4);
}

#line 271 "/app/tests/_auto_numeric_intrinsics.py"
float test_WaveActiveMax_Float()
{
	return WaveActiveMax(g_f);
}

#line 274 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WaveActiveMax_Float1()
{
	return WaveActiveMax(g_f1);
}

#line 277 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WaveActiveMax_Float2()
{
	return WaveActiveMax(g_f2);
}

#line 280 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WaveActiveMax_Float3()
{
	return WaveActiveMax(g_f3);
}

#line 283 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WaveActiveMax_Float4()
{
	return WaveActiveMax(g_f4);
}

#line 286 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WaveActiveMax_Float1x1()
{
	return WaveActiveMax(g_f1x1);
}

#line 289 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WaveActiveMax_Float1x2()
{
	return WaveActiveMax(g_f1x2);
}

#line 292 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WaveActiveMax_Float1x3()
{
	return WaveActiveMax(g_f1x3);
}

#line 295 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WaveActiveMax_Float1x4()
{
	return WaveActiveMax(g_f1x4);
}

#line 298 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WaveActiveMax_Float2x1()
{
	return WaveActiveMax(g_f2x1);
}

#line 301 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WaveActiveMax_Float2x2()
{
	return WaveActiveMax(g_f2x2);
}

#line 304 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WaveActiveMax_Float2x3()
{
	return WaveActiveMax(g_f2x3);
}

#line 307 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WaveActiveMax_Float2x4()
{
	return WaveActiveMax(g_f2x4);
}

#line 310 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WaveActiveMax_Float3x1()
{
	return WaveActiveMax(g_f3x1);
}

#line 313 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WaveActiveMax_Float3x2()
{
	return WaveActiveMax(g_f3x2);
}

#line 316 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WaveActiveMax_Float3x3()
{
	return WaveActiveMax(g_f3x3);
}

#line 319 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WaveActiveMax_Float3x4()
{
	return WaveActiveMax(g_f3x4);
}

#line 322 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WaveActiveMax_Float4x1()
{
	return WaveActiveMax(g_f4x1);
}

#line 325 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WaveActiveMax_Float4x2()
{
	return WaveActiveMax(g_f4x2);
}

#line 328 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WaveActiveMax_Float4x3()
{
	return WaveActiveMax(g_f4x3);
}

#line 331 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WaveActiveMax_Float4x4()
{
	return WaveActiveMax(g_f4x4);
}

#line 334 "/app/tests/_auto_numeric_intrinsics.py"
float test_WaveActiveMin_Float()
{
	return WaveActiveMin(g_f);
}

#line 337 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WaveActiveMin_Float1()
{
	return WaveActiveMin(g_f1);
}

#line 340 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WaveActiveMin_Float2()
{
	return WaveActiveMin(g_f2);
}

#line 343 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WaveActiveMin_Float3()
{
	return WaveActiveMin(g_f3);
}

#line 346 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WaveActiveMin_Float4()
{
	return WaveActiveMin(g_f4);
}

#line 349 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WaveActiveMin_Float1x1()
{
	return WaveActiveMin(g_f1x1);
}

#line 352 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WaveActiveMin_Float1x2()
{
	return WaveActiveMin(g_f1x2);
}

#line 355 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WaveActiveMin_Float1x3()
{
	return WaveActiveMin(g_f1x3);
}

#line 358 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WaveActiveMin_Float1x4()
{
	return WaveActiveMin(g_f1x4);
}

#line 361 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WaveActiveMin_Float2x1()
{
	return WaveActiveMin(g_f2x1);
}

#line 364 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WaveActiveMin_Float2x2()
{
	return WaveActiveMin(g_f2x2);
}

#line 367 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WaveActiveMin_Float2x3()
{
	return WaveActiveMin(g_f2x3);
}

#line 370 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WaveActiveMin_Float2x4()
{
	return WaveActiveMin(g_f2x4);
}

#line 373 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WaveActiveMin_Float3x1()
{
	return WaveActiveMin(g_f3x1);
}

#line 376 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WaveActiveMin_Float3x2()
{
	return WaveActiveMin(g_f3x2);
}

#line 379 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WaveActiveMin_Float3x3()
{
	return WaveActiveMin(g_f3x3);
}

#line 382 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WaveActiveMin_Float3x4()
{
	return WaveActiveMin(g_f3x4);
}

#line 385 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WaveActiveMin_Float4x1()
{
	return WaveActiveMin(g_f4x1);
}

#line 388 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WaveActiveMin_Float4x2()
{
	return WaveActiveMin(g_f4x2);
}

#line 391 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WaveActiveMin_Float4x3()
{
	return WaveActiveMin(g_f4x3);
}

#line 394 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WaveActiveMin_Float4x4()
{
	return WaveActiveMin(g_f4x4);
}

#line 397 "/app/tests/_auto_numeric_intrinsics.py"
float test_WaveActiveProduct_Float()
{
	return WaveActiveProduct(g_f);
}

#line 400 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WaveActiveProduct_Float1()
{
	return WaveActiveProduct(g_f1);
}

#line 403 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WaveActiveProduct_Float2()
{
	return WaveActiveProduct(g_f2);
}

#line 406 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WaveActiveProduct_Float3()
{
	return WaveActiveProduct(g_f3);
}

#line 409 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WaveActiveProduct_Float4()
{
	return WaveActiveProduct(g_f4);
}

#line 412 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WaveActiveProduct_Float1x1()
{
	return WaveActiveProduct(g_f1x1);
}

#line 415 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WaveActiveProduct_Float1x2()
{
	return WaveActiveProduct(g_f1x2);
}

#line 418 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WaveActiveProduct_Float1x3()
{
	return WaveActiveProduct(g_f1x3);
}

#line 421 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WaveActiveProduct_Float1x4()
{
	return WaveActiveProduct(g_f1x4);
}

#line 424 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WaveActiveProduct_Float2x1()
{
	return WaveActiveProduct(g_f2x1);
}

#line 427 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WaveActiveProduct_Float2x2()
{
	return WaveActiveProduct(g_f2x2);
}

#line 430 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WaveActiveProduct_Float2x3()
{
	return WaveActiveProduct(g_f2x3);
}

#line 433 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WaveActiveProduct_Float2x4()
{
	return WaveActiveProduct(g_f2x4);
}

#line 436 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WaveActiveProduct_Float3x1()
{
	return WaveActiveProduct(g_f3x1);
}

#line 439 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WaveActiveProduct_Float3x2()
{
	return WaveActiveProduct(g_f3x2);
}

#line 442 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WaveActiveProduct_Float3x3()
{
	return WaveActiveProduct(g_f3x3);
}

#line 445 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WaveActiveProduct_Float3x4()
{
	return WaveActiveProduct(g_f3x4);
}

#line 448 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WaveActiveProduct_Float4x1()
{
	return WaveActiveProduct(g_f4x1);
}

#line 451 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WaveActiveProduct_Float4x2()
{
	return WaveActiveProduct(g_f4x2);
}

#line 454 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WaveActiveProduct_Float4x3()
{
	return WaveActiveProduct(g_f4x3);
}

#line 457 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WaveActiveProduct_Float4x4()
{
	return WaveActiveProduct(g_f4x4);
}

#line 460 "/app/tests/_auto_numeric_intrinsics.py"
float test_WaveActiveSum_Float()
{
	return WaveActiveSum(g_f);
}

#line 463 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WaveActiveSum_Float1()
{
	return WaveActiveSum(g_f1);
}

#line 466 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WaveActiveSum_Float2()
{
	return WaveActiveSum(g_f2);
}

#line 469 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WaveActiveSum_Float3()
{
	return WaveActiveSum(g_f3);
}

#line 472 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WaveActiveSum_Float4()
{
	return WaveActiveSum(g_f4);
}

#line 475 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WaveActiveSum_Float1x1()
{
	return WaveActiveSum(g_f1x1);
}

#line 478 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WaveActiveSum_Float1x2()
{
	return WaveActiveSum(g_f1x2);
}

#line 481 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WaveActiveSum_Float1x3()
{
	return WaveActiveSum(g_f1x3);
}

#line 484 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WaveActiveSum_Float1x4()
{
	return WaveActiveSum(g_f1x4);
}

#line 487 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WaveActiveSum_Float2x1()
{
	return WaveActiveSum(g_f2x1);
}

#line 490 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WaveActiveSum_Float2x2()
{
	return WaveActiveSum(g_f2x2);
}

#line 493 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WaveActiveSum_Float2x3()
{
	return WaveActiveSum(g_f2x3);
}

#line 496 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WaveActiveSum_Float2x4()
{
	return WaveActiveSum(g_f2x4);
}

#line 499 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WaveActiveSum_Float3x1()
{
	return WaveActiveSum(g_f3x1);
}

#line 502 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WaveActiveSum_Float3x2()
{
	return WaveActiveSum(g_f3x2);
}

#line 505 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WaveActiveSum_Float3x3()
{
	return WaveActiveSum(g_f3x3);
}

#line 508 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WaveActiveSum_Float3x4()
{
	return WaveActiveSum(g_f3x4);
}

#line 511 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WaveActiveSum_Float4x1()
{
	return WaveActiveSum(g_f4x1);
}

#line 514 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WaveActiveSum_Float4x2()
{
	return WaveActiveSum(g_f4x2);
}

#line 517 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WaveActiveSum_Float4x3()
{
	return WaveActiveSum(g_f4x3);
}

#line 520 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WaveActiveSum_Float4x4()
{
	return WaveActiveSum(g_f4x4);
}

#line 523 "/app/tests/_auto_numeric_intrinsics.py"
float test_WavePrefixProduct_Float()
{
	return WavePrefixProduct(g_f);
}

#line 526 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WavePrefixProduct_Float1()
{
	return WavePrefixProduct(g_f1);
}

#line 529 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WavePrefixProduct_Float2()
{
	return WavePrefixProduct(g_f2);
}

#line 532 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WavePrefixProduct_Float3()
{
	return WavePrefixProduct(g_f3);
}

#line 535 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WavePrefixProduct_Float4()
{
	return WavePrefixProduct(g_f4);
}

#line 538 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WavePrefixProduct_Float1x1()
{
	return WavePrefixProduct(g_f1x1);
}

#line 541 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WavePrefixProduct_Float1x2()
{
	return WavePrefixProduct(g_f1x2);
}

#line 544 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WavePrefixProduct_Float1x3()
{
	return WavePrefixProduct(g_f1x3);
}

#line 547 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WavePrefixProduct_Float1x4()
{
	return WavePrefixProduct(g_f1x4);
}

#line 550 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WavePrefixProduct_Float2x1()
{
	return WavePrefixProduct(g_f2x1);
}

#line 553 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WavePrefixProduct_Float2x2()
{
	return WavePrefixProduct(g_f2x2);
}

#line 556 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WavePrefixProduct_Float2x3()
{
	return WavePrefixProduct(g_f2x3);
}

#line 559 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WavePrefixProduct_Float2x4()
{
	return WavePrefixProduct(g_f2x4);
}

#line 562 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WavePrefixProduct_Float3x1()
{
	return WavePrefixProduct(g_f3x1);
}

#line 565 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WavePrefixProduct_Float3x2()
{
	return WavePrefixProduct(g_f3x2);
}

#line 568 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WavePrefixProduct_Float3x3()
{
	return WavePrefixProduct(g_f3x3);
}

#line 571 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WavePrefixProduct_Float3x4()
{
	return WavePrefixProduct(g_f3x4);
}

#line 574 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WavePrefixProduct_Float4x1()
{
	return WavePrefixProduct(g_f4x1);
}

#line 577 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WavePrefixProduct_Float4x2()
{
	return WavePrefixProduct(g_f4x2);
}

#line 580 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WavePrefixProduct_Float4x3()
{
	return WavePrefixProduct(g_f4x3);
}

#line 583 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WavePrefixProduct_Float4x4()
{
	return WavePrefixProduct(g_f4x4);
}

#line 586 "/app/tests/_auto_numeric_intrinsics.py"
float test_WavePrefixSum_Float()
{
	return WavePrefixSum(g_f);
}

#line 589 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_WavePrefixSum_Float1()
{
	return WavePrefixSum(g_f1);
}

#line 592 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_WavePrefixSum_Float2()
{
	return WavePrefixSum(g_f2);
}

#line 595 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_WavePrefixSum_Float3()
{
	return WavePrefixSum(g_f3);
}

#line 598 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_WavePrefixSum_Float4()
{
	return WavePrefixSum(g_f4);
}

#line 601 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_WavePrefixSum_Float1x1()
{
	return WavePrefixSum(g_f1x1);
}

#line 604 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_WavePrefixSum_Float1x2()
{
	return WavePrefixSum(g_f1x2);
}

#line 607 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_WavePrefixSum_Float1x3()
{
	return WavePrefixSum(g_f1x3);
}

#line 610 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_WavePrefixSum_Float1x4()
{
	return WavePrefixSum(g_f1x4);
}

#line 613 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_WavePrefixSum_Float2x1()
{
	return WavePrefixSum(g_f2x1);
}

#line 616 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_WavePrefixSum_Float2x2()
{
	return WavePrefixSum(g_f2x2);
}

#line 619 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_WavePrefixSum_Float2x3()
{
	return WavePrefixSum(g_f2x3);
}

#line 622 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_WavePrefixSum_Float2x4()
{
	return WavePrefixSum(g_f2x4);
}

#line 625 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_WavePrefixSum_Float3x1()
{
	return WavePrefixSum(g_f3x1);
}

#line 628 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_WavePrefixSum_Float3x2()
{
	return WavePrefixSum(g_f3x2);
}

#line 631 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_WavePrefixSum_Float3x3()
{
	return WavePrefixSum(g_f3x3);
}

#line 634 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_WavePrefixSum_Float3x4()
{
	return WavePrefixSum(g_f3x4);
}

#line 637 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_WavePrefixSum_Float4x1()
{
	return WavePrefixSum(g_f4x1);
}

#line 640 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_WavePrefixSum_Float4x2()
{
	return WavePrefixSum(g_f4x2);
}

#line 643 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_WavePrefixSum_Float4x3()
{
	return WavePrefixSum(g_f4x3);
}

#line 646 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_WavePrefixSum_Float4x4()
{
	return WavePrefixSum(g_f4x4);
}

#line 649 "/app/tests/_auto_numeric_intrinsics.py"
float test_abs_Float()
{
	return abs(g_f);
}

#line 652 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_abs_Float1()
{
	return abs(g_f1);
}

#line 655 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_abs_Float2()
{
	return abs(g_f2);
}

#line 658 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_abs_Float3()
{
	return abs(g_f3);
}

#line 661 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_abs_Float4()
{
	return abs(g_f4);
}

#line 664 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_abs_Float1x1()
{
	return abs(g_f1x1);
}

#line 667 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_abs_Float1x2()
{
	return abs(g_f1x2);
}

#line 670 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_abs_Float1x3()
{
	return abs(g_f1x3);
}

#line 673 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_abs_Float1x4()
{
	return abs(g_f1x4);
}

#line 676 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_abs_Float2x1()
{
	return abs(g_f2x1);
}

#line 679 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_abs_Float2x2()
{
	return abs(g_f2x2);
}

#line 682 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_abs_Float2x3()
{
	return abs(g_f2x3);
}

#line 685 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_abs_Float2x4()
{
	return abs(g_f2x4);
}

#line 688 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_abs_Float3x1()
{
	return abs(g_f3x1);
}

#line 691 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_abs_Float3x2()
{
	return abs(g_f3x2);
}

#line 694 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_abs_Float3x3()
{
	return abs(g_f3x3);
}

#line 697 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_abs_Float3x4()
{
	return abs(g_f3x4);
}

#line 700 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_abs_Float4x1()
{
	return abs(g_f4x1);
}

#line 703 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_abs_Float4x2()
{
	return abs(g_f4x2);
}

#line 706 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_abs_Float4x3()
{
	return abs(g_f4x3);
}

#line 709 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_abs_Float4x4()
{
	return abs(g_f4x4);
}

#line 712 "/app/tests/_auto_numeric_intrinsics.py"
float test_clamp_Float(float min, float max)
{
	return clamp(g_f, min, max);
}

#line 715 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_clamp_Float1(float1 min, float1 max)
{
	return clamp(g_f1, min, max);
}

#line 718 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_clamp_Float2(float2 min, float2 max)
{
	return clamp(g_f2, min, max);
}

#line 721 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_clamp_Float3(float3 min, float3 max)
{
	return clamp(g_f3, min, max);
}

#line 724 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_clamp_Float4(float4 min, float4 max)
{
	return clamp(g_f4, min, max);
}

#line 727 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_clamp_Float1x1(float1x1 min, float1x1 max)
{
	return clamp(g_f1x1, min, max);
}

#line 730 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_clamp_Float1x2(float1x2 min, float1x2 max)
{
	return clamp(g_f1x2, min, max);
}

#line 733 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_clamp_Float1x3(float1x3 min, float1x3 max)
{
	return clamp(g_f1x3, min, max);
}

#line 736 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_clamp_Float1x4(float1x4 min, float1x4 max)
{
	return clamp(g_f1x4, min, max);
}

#line 739 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_clamp_Float2x1(float2x1 min, float2x1 max)
{
	return clamp(g_f2x1, min, max);
}

#line 742 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_clamp_Float2x2(float2x2 min, float2x2 max)
{
	return clamp(g_f2x2, min, max);
}

#line 745 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_clamp_Float2x3(float2x3 min, float2x3 max)
{
	return clamp(g_f2x3, min, max);
}

#line 748 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_clamp_Float2x4(float2x4 min, float2x4 max)
{
	return clamp(g_f2x4, min, max);
}

#line 751 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_clamp_Float3x1(float3x1 min, float3x1 max)
{
	return clamp(g_f3x1, min, max);
}

#line 754 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_clamp_Float3x2(float3x2 min, float3x2 max)
{
	return clamp(g_f3x2, min, max);
}

#line 757 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_clamp_Float3x3(float3x3 min, float3x3 max)
{
	return clamp(g_f3x3, min, max);
}

#line 760 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_clamp_Float3x4(float3x4 min, float3x4 max)
{
	return clamp(g_f3x4, min, max);
}

#line 763 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_clamp_Float4x1(float4x1 min, float4x1 max)
{
	return clamp(g_f4x1, min, max);
}

#line 766 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_clamp_Float4x2(float4x2 min, float4x2 max)
{
	return clamp(g_f4x2, min, max);
}

#line 769 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_clamp_Float4x3(float4x3 min, float4x3 max)
{
	return clamp(g_f4x3, min, max);
}

#line 772 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_clamp_Float4x4(float4x4 min, float4x4 max)
{
	return clamp(g_f4x4, min, max);
}

#line 775 "/app/tests/_auto_numeric_intrinsics.py"
float test_mad_Float(float b, float c)
{
	return mad(g_f, b, c);
}

#line 778 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_mad_Float1(float1 b, float1 c)
{
	return mad(g_f1, b, c);
}

#line 781 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_mad_Float2(float2 b, float2 c)
{
	return mad(g_f2, b, c);
}

#line 784 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_mad_Float3(float3 b, float3 c)
{
	return mad(g_f3, b, c);
}

#line 787 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_mad_Float4(float4 b, float4 c)
{
	return mad(g_f4, b, c);
}

#line 790 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_mad_Float1x1(float1x1 b, float1x1 c)
{
	return mad(g_f1x1, b, c);
}

#line 793 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_mad_Float1x2(float1x2 b, float1x2 c)
{
	return mad(g_f1x2, b, c);
}

#line 796 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_mad_Float1x3(float1x3 b, float1x3 c)
{
	return mad(g_f1x3, b, c);
}

#line 799 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_mad_Float1x4(float1x4 b, float1x4 c)
{
	return mad(g_f1x4, b, c);
}

#line 802 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_mad_Float2x1(float2x1 b, float2x1 c)
{
	return mad(g_f2x1, b, c);
}

#line 805 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_mad_Float2x2(float2x2 b, float2x2 c)
{
	return mad(g_f2x2, b, c);
}

#line 808 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_mad_Float2x3(float2x3 b, float2x3 c)
{
	return mad(g_f2x3, b, c);
}

#line 811 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_mad_Float2x4(float2x4 b, float2x4 c)
{
	return mad(g_f2x4, b, c);
}

#line 814 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_mad_Float3x1(float3x1 b, float3x1 c)
{
	return mad(g_f3x1, b, c);
}

#line 817 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_mad_Float3x2(float3x2 b, float3x2 c)
{
	return mad(g_f3x2, b, c);
}

#line 820 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_mad_Float3x3(float3x3 b, float3x3 c)
{
	return mad(g_f3x3, b, c);
}

#line 823 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_mad_Float3x4(float3x4 b, float3x4 c)
{
	return mad(g_f3x4, b, c);
}

#line 826 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_mad_Float4x1(float4x1 b, float4x1 c)
{
	return mad(g_f4x1, b, c);
}

#line 829 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_mad_Float4x2(float4x2 b, float4x2 c)
{
	return mad(g_f4x2, b, c);
}

#line 832 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_mad_Float4x3(float4x3 b, float4x3 c)
{
	return mad(g_f4x3, b, c);
}

#line 835 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_mad_Float4x4(float4x4 b, float4x4 c)
{
	return mad(g_f4x4, b, c);
}

#line 838 "/app/tests/_auto_numeric_intrinsics.py"
float test_max_Float(float b)
{
	return max(g_f, b);
}

#line 841 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_max_Float1(float1 b)
{
	return max(g_f1, b);
}

#line 844 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_max_Float2(float2 b)
{
	return max(g_f2, b);
}

#line 847 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_max_Float3(float3 b)
{
	return max(g_f3, b);
}

#line 850 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_max_Float4(float4 b)
{
	return max(g_f4, b);
}

#line 853 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_max_Float1x1(float1x1 b)
{
	return max(g_f1x1, b);
}

#line 856 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_max_Float1x2(float1x2 b)
{
	return max(g_f1x2, b);
}

#line 859 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_max_Float1x3(float1x3 b)
{
	return max(g_f1x3, b);
}

#line 862 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_max_Float1x4(float1x4 b)
{
	return max(g_f1x4, b);
}

#line 865 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_max_Float2x1(float2x1 b)
{
	return max(g_f2x1, b);
}

#line 868 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_max_Float2x2(float2x2 b)
{
	return max(g_f2x2, b);
}

#line 871 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_max_Float2x3(float2x3 b)
{
	return max(g_f2x3, b);
}

#line 874 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_max_Float2x4(float2x4 b)
{
	return max(g_f2x4, b);
}

#line 877 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_max_Float3x1(float3x1 b)
{
	return max(g_f3x1, b);
}

#line 880 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_max_Float3x2(float3x2 b)
{
	return max(g_f3x2, b);
}

#line 883 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_max_Float3x3(float3x3 b)
{
	return max(g_f3x3, b);
}

#line 886 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_max_Float3x4(float3x4 b)
{
	return max(g_f3x4, b);
}

#line 889 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_max_Float4x1(float4x1 b)
{
	return max(g_f4x1, b);
}

#line 892 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_max_Float4x2(float4x2 b)
{
	return max(g_f4x2, b);
}

#line 895 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_max_Float4x3(float4x3 b)
{
	return max(g_f4x3, b);
}

#line 898 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_max_Float4x4(float4x4 b)
{
	return max(g_f4x4, b);
}

#line 901 "/app/tests/_auto_numeric_intrinsics.py"
float test_min_Float(float b)
{
	return min(g_f, b);
}

#line 904 "/app/tests/_auto_numeric_intrinsics.py"
float1 test_min_Float1(float1 b)
{
	return min(g_f1, b);
}

#line 907 "/app/tests/_auto_numeric_intrinsics.py"
float2 test_min_Float2(float2 b)
{
	return min(g_f2, b);
}

#line 910 "/app/tests/_auto_numeric_intrinsics.py"
float3 test_min_Float3(float3 b)
{
	return min(g_f3, b);
}

#line 913 "/app/tests/_auto_numeric_intrinsics.py"
float4 test_min_Float4(float4 b)
{
	return min(g_f4, b);
}

#line 916 "/app/tests/_auto_numeric_intrinsics.py"
float1x1 test_min_Float1x1(float1x1 b)
{
	return min(g_f1x1, b);
}

#line 919 "/app/tests/_auto_numeric_intrinsics.py"
float1x2 test_min_Float1x2(float1x2 b)
{
	return min(g_f1x2, b);
}

#line 922 "/app/tests/_auto_numeric_intrinsics.py"
float1x3 test_min_Float1x3(float1x3 b)
{
	return min(g_f1x3, b);
}

#line 925 "/app/tests/_auto_numeric_intrinsics.py"
float1x4 test_min_Float1x4(float1x4 b)
{
	return min(g_f1x4, b);
}

#line 928 "/app/tests/_auto_numeric_intrinsics.py"
float2x1 test_min_Float2x1(float2x1 b)
{
	return min(g_f2x1, b);
}

#line 931 "/app/tests/_auto_numeric_intrinsics.py"
float2x2 test_min_Float2x2(float2x2 b)
{
	return min(g_f2x2, b);
}

#line 934 "/app/tests/_auto_numeric_intrinsics.py"
float2x3 test_min_Float2x3(float2x3 b)
{
	return min(g_f2x3, b);
}

#line 937 "/app/tests/_auto_numeric_intrinsics.py"
float2x4 test_min_Float2x4(float2x4 b)
{
	return min(g_f2x4, b);
}

#line 940 "/app/tests/_auto_numeric_intrinsics.py"
float3x1 test_min_Float3x1(float3x1 b)
{
	return min(g_f3x1, b);
}

#line 943 "/app/tests/_auto_numeric_intrinsics.py"
float3x2 test_min_Float3x2(float3x2 b)
{
	return min(g_f3x2, b);
}

#line 946 "/app/tests/_auto_numeric_intrinsics.py"
float3x3 test_min_Float3x3(float3x3 b)
{
	return min(g_f3x3, b);
}

#line 949 "/app/tests/_auto_numeric_intrinsics.py"
float3x4 test_min_Float3x4(float3x4 b)
{
	return min(g_f3x4, b);
}

#line 952 "/app/tests/_auto_numeric_intrinsics.py"
float4x1 test_min_Float4x1(float4x1 b)
{
	return min(g_f4x1, b);
}

#line 955 "/app/tests/_auto_numeric_intrinsics.py"
float4x2 test_min_Float4x2(float4x2 b)
{
	return min(g_f4x2, b);
}

#line 958 "/app/tests/_auto_numeric_intrinsics.py"
float4x3 test_min_Float4x3(float4x3 b)
{
	return min(g_f4x3, b);
}

#line 961 "/app/tests/_auto_numeric_intrinsics.py"
float4x4 test_min_Float4x4(float4x4 b)
{
	return min(g_f4x4, b);
}

