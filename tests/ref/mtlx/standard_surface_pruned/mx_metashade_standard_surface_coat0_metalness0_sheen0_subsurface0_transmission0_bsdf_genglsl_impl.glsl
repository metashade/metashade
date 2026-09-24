#include "mx_dielectric_bsdf.glsl"
#include "mx_layer_bsdf.glsl"
#include "mx_mix_bsdf.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_roughness_anisotropy.glsl"
// Rodrigues' rotation formula.
// 
// Private copy of the stdlib rotate3d helper.  Avoids
// duplicate-definition errors when the material's own nodegraph
// also uses rotate3d nodes, which would cause the generator to
// emit mx_rotate_vector3 a second time
// (see https://github.com/metashade/metashade/issues/230).
//
vec3 _mx_metashade_rotate_vector3(vec3 in_, float amount, vec3 axis)
{
	vec3 axis_n = normalize(axis);
	float rad = radians(amount);
	float s = sin(rad);
	float c = cos(rad);
	return ((in_ * c) + (cross(in_, axis_n) * s)) + ((axis_n * dot(axis_n, in_)) * (1 - c));
}

// Conditionally rotate a tangent vector when anisotropy is active.
//
vec3 _mx_metashade_rotate_tangent(vec3 tangent, float anisotropy, float rotation, vec3 axis)
{
	if (anisotropy > 0.0)
	{
		float rotate_degree = rotation * 360.0;
		return normalize(_mx_metashade_rotate_vector3(tangent, rotate_degree, axis));
	}
	return tangent;
}

void mx_metashade_standard_surface_coat0_metalness0_sheen0_subsurface0_transmission0_bsdf(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float specular_rotation, float thin_film_thickness, float thin_film_IOR, vec3 normal, vec3 tangent, inout BSDF bsdf)
{
	// 
	// Roughness
	vec2 main_roughness;
	mx_roughness_anisotropy(specular_roughness, specular_anisotropy, main_roughness);
	// 
	// Tangent rotation
	vec3 main_tangent = _mx_metashade_rotate_tangent(tangent, specular_anisotropy, specular_rotation, normal);
	// 
	// Diffuse BSDF (Oren-Nayar)
	{
		BSDF diffuse_bsdf = BSDF(vec3(0), vec3(1));
		// `energy_compensation=false` to match the Standard Surface spec, 
		// instead of the more physically-correct `true` in OpenPBR
		mx_oren_nayar_diffuse_bsdf(closureData, base, base_color, diffuse_roughness, normal, false, diffuse_bsdf);
		bsdf = diffuse_bsdf;
	}
	// 
	// Specular BSDF (dielectric reflection)
	{
		BSDF specular_bsdf = BSDF(vec3(0), vec3(1));
		mx_dielectric_bsdf(closureData, specular, specular_color, specular_IOR, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, main_tangent, 0, 0, specular_bsdf);
		mx_layer_bsdf(closureData, specular_bsdf, bsdf, bsdf);
	}
}

