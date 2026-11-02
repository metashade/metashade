// Color of the Julia set of z^2 + c, a placeholder returning hot pink.
// 
// Args:
// texcoord: Point in the complex plane, before scaling
// cx: Real part of the constant c
// cy: Imaginary part of the constant c
// scale: Extent of the complex plane per unit of texcoord
// max_iterations: Maximum number of iterations of z^2 + c
// phase: Offset of the color palette
//
vec3 julia2d(vec2 texcoord, float cx, float cy, float scale, int max_iterations, float phase)
{
	return vec3(1.0, 0.0, 0.5);
}

void mx_julia2d_color3(vec2 texcoord, float cx, float cy, float scale, int max_iterations, float phase, out vec3 out_)
{
	out_ = julia2d(texcoord, cx, cy, scale, max_iterations, phase);
}

