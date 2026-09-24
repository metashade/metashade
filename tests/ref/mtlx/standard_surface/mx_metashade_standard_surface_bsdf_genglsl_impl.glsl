#include "mx_artistic_ior.glsl"
#include "mx_conductor_bsdf.glsl"
#include "mx_dielectric_bsdf.glsl"
#include "mx_layer_bsdf.glsl"
#include "mx_mix_bsdf.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_roughness_anisotropy.glsl"
#include "mx_sheen_bsdf.glsl"
#include "mx_subsurface_bsdf.glsl"
#include "mx_translucent_bsdf.glsl"
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

void mx_metashade_standard_surface_bsdf(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float metalness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float specular_rotation, float transmission, vec3 transmission_color, float transmission_extra_roughness, float subsurface, vec3 subsurface_color, vec3 subsurface_radius, float subsurface_scale, float subsurface_anisotropy, float sheen, vec3 sheen_color, float sheen_roughness, float coat, vec3 coat_color, float coat_roughness, float coat_anisotropy, float coat_rotation, float coat_IOR, vec3 coat_normal, float coat_affect_color, float coat_affect_roughness, float thin_film_thickness, float thin_film_IOR, bool thin_walled, vec3 normal, vec3 tangent, inout BSDF bsdf)
{
	// 
	// Coat affect roughness: blend specular roughness toward 1.0
	float coat_roughness_factor = (coat_affect_roughness * coat) * coat_roughness;
	float coat_affected_specular_roughness = mix(specular_roughness, 1, coat_roughness_factor);
	// 
	// Roughness
	vec2 main_roughness;
	mx_roughness_anisotropy(coat_affected_specular_roughness, specular_anisotropy, main_roughness);
	// 
	// Tangent rotation
	vec3 main_tangent = _mx_metashade_rotate_tangent(tangent, specular_anisotropy, specular_rotation, normal);
	// 
	// Coat tangent rotation
	vec3 coat_tangent = _mx_metashade_rotate_tangent(tangent, coat_anisotropy, coat_rotation, coat_normal);
	// 
	// Coat affect color: darken diffuse under the coat
	vec3 coat_gamma = vec3((clamp(coat, 0.0, 1.0) * coat_affect_color) + 1.0);
	vec3 coat_affected_diffuse_color = pow(clamp(base_color, 0.0, 1.0), coat_gamma);
	// 
	// Coat affect subsurface color
	subsurface_color = pow(clamp(subsurface_color, 0.0, 1.0), coat_gamma);
	// 
	// Diffuse BSDF (Oren-Nayar)
	{
		BSDF diffuse_bsdf = BSDF(vec3(0), vec3(1));
		// `energy_compensation=false` to match the Standard Surface spec, 
		// instead of the more physically-correct `true` in OpenPBR
		mx_oren_nayar_diffuse_bsdf(closureData, base, coat_affected_diffuse_color, diffuse_roughness, normal, false, diffuse_bsdf);
		bsdf = diffuse_bsdf;
	}
	// 
	// Subsurface scattering
	{
		vec3 subsurface_radius_scaled = subsurface_radius * subsurface_scale;
		BSDF sss_bsdf = BSDF(vec3(0), vec3(1));
		if (thin_walled)
		{
			mx_translucent_bsdf(closureData, 1.0, subsurface_color, normal, sss_bsdf);
		}
		else
		{
			mx_subsurface_bsdf(closureData, 1.0, subsurface_color, subsurface_radius_scaled, subsurface_anisotropy, normal, sss_bsdf);
		}
		mx_mix_bsdf(closureData, sss_bsdf, bsdf, subsurface, bsdf);
	}
	// 
	// Sheen BSDF
	{
		BSDF sheen_bsdf_out = BSDF(vec3(0), vec3(1));
		mx_sheen_bsdf(closureData, sheen, sheen_color, sheen_roughness, normal, 0, sheen_bsdf_out);
		mx_layer_bsdf(closureData, sheen_bsdf_out, bsdf, bsdf);
	}
	// 
	// Transmission
	{
		float transmission_roughness_scalar = clamp(specular_roughness + transmission_extra_roughness, 0.0, 1.0);
		// Coat-affected
		transmission_roughness_scalar = mix(transmission_roughness_scalar, 1, coat_roughness_factor);
		vec2 transmission_roughness;
		mx_roughness_anisotropy(transmission_roughness_scalar, specular_anisotropy, transmission_roughness);
		// 
		// Transmission BSDF (dielectric transmission)
		BSDF transmission_bsdf = BSDF(vec3(0), vec3(1));
		mx_dielectric_bsdf(closureData, 1.0, transmission_color, specular_IOR, transmission_roughness, false, 0.0, 1.5, normal, main_tangent, 0, 1, transmission_bsdf);
		mx_mix_bsdf(closureData, transmission_bsdf, bsdf, transmission, bsdf);
	}
	// 
	// Specular BSDF (dielectric reflection)
	{
		BSDF specular_bsdf = BSDF(vec3(0), vec3(1));
		mx_dielectric_bsdf(closureData, specular, specular_color, specular_IOR, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, main_tangent, 0, 0, specular_bsdf);
		mx_layer_bsdf(closureData, specular_bsdf, bsdf, bsdf);
	}
	// 
	// Metalness
	{
		// Artistic IOR (reflectivity/edge-color -> physical IOR/extinction)
		vec3 metal_reflectivity = base_color * base;
		vec3 metal_edgecolor = specular_color * specular;
		vec3 ior_n;
		vec3 ior_k;
		mx_artistic_ior(metal_reflectivity, metal_edgecolor, ior_n, ior_k);
		// 
		// Conductor BSDF (metal reflection)
		BSDF metal_bsdf = BSDF(vec3(0), vec3(1));
		mx_conductor_bsdf(closureData, metalness, ior_n, ior_k, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, main_tangent, 0, metal_bsdf);
		// 
		// Metalness mix: conductor (fg) vs specular layer (bg)
		// Conductor response is already scaled by metalness (the weight),
		// so we just add it to the attenuated specular layer.
		float one_minus_metalness = 1 - metalness;
		bsdf.response = metal_bsdf.response + (bsdf.response * one_minus_metalness);
		bsdf.throughput = metal_bsdf.throughput + (bsdf.throughput * one_minus_metalness);
	}
	// 
	// Coat attenuation and layer
	{
		vec3 coat_attenuation = mix(vec3(1.0), coat_color, coat);
		bsdf.response *= coat_attenuation;
		bsdf.throughput *= coat_attenuation;
		// 
		// Coat roughness
		vec2 coat_roughness_vec;
		mx_roughness_anisotropy(coat_roughness, coat_anisotropy, coat_roughness_vec);
		// 
		// Coat BSDF (dielectric reflection)
		BSDF coat_bsdf = BSDF(vec3(0), vec3(1));
		mx_dielectric_bsdf(closureData, coat, vec3(1.0), coat_IOR, coat_roughness_vec, false, 0.0, 1.5, coat_normal, coat_tangent, 0, 0, coat_bsdf);
		mx_layer_bsdf(closureData, coat_bsdf, bsdf, bsdf);
	}
}

