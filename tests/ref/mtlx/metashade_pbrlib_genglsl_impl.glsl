// Metashade wrapper for generalized_schlick_bsdf (stub).
// 
// This is a simplified stub to validate the override infrastructure.
// The full implementation will match MaterialX's signature:
// - ClosureData closureData
// - float weight
// - vec3 color0, color82, color90
// - float exponent
// - vec2 roughness
// - float thinfilm_thickness, thinfilm_ior
// - vec3 N, X
// - int distribution, scatter_mode
// - inout BSDF bsdf
// 
// For now, just returns color0 scaled by weight.
//
void mx_metashade_generalized_schlick_bsdf(float weight, vec3 color0, vec3 color90, float exponent, out vec3 result)
{
	result = color0 * weight;
}

