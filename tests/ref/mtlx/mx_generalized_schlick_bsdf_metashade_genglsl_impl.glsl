#include "mx_generalized_schlick_bsdf.glsl"
void mx_generalized_schlick_bsdf_metashade(ClosureData closureData, float weight, vec3 color0, vec3 color82, vec3 color90, float exponent, vec2 roughness, float thinfilm_thickness, float thinfilm_ior, vec3 normal, vec3 tangent, int distribution, int scatter_mode, out BSDF out_)
{
	mx_generalized_schlick_bsdf(closureData, weight, color0, color82, color90, exponent, roughness, thinfilm_thickness, thinfilm_ior, normal, tangent, distribution, scatter_mode, out_);
}

