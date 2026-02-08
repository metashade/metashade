#include "mx_fractal3d_float.glsl"
void mx_fractal3d_float_metashade(float amplitude, int octaves, float lacunarity, float diminish, vec3 position, out float out_)
{
	mx_fractal3d_float(amplitude, octaves, lacunarity, diminish, position, out_);
}

