#include "mx_generalized_schlick_bsdf.glsl"
void mx_generalized_schlick_bsdf_broken(ClosureData closureData, float weight, vec3 color0, vec3 color82, vec3 color90, float exponent, vec2 roughness, bool retroreflective, float thinfilm_thickness, float thinfilm_ior, vec3 normal, vec3 tangent, int distribution, int scatter_mode, out BSDF out_)
{
	out_.response = vec3(1.0, 0.0, 0.5);
	out_.throughput = vec3(0.0, 0.0, 0.0);
}

