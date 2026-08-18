#include "mx_roughness_anisotropy.glsl"
#include "mx_rotate_vector3.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_translucent_bsdf.glsl"
#include "mx_subsurface_bsdf.glsl"
#include "mx_sheen_bsdf.glsl"
#include "mx_dielectric_bsdf.glsl"
#include "mx_conductor_bsdf.glsl"
#include "mx_artistic_ior.glsl"
void mx_metashade_standard_surface_bsdf(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float metalness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float specular_rotation, float transmission, vec3 transmission_color, float transmission_extra_roughness, float subsurface, vec3 subsurface_color, vec3 subsurface_radius, float subsurface_scale, float subsurface_anisotropy, float sheen, vec3 sheen_color, float sheen_roughness, float coat, vec3 coat_color, float coat_roughness, float coat_anisotropy, float coat_rotation, float coat_IOR, vec3 coat_normal, float coat_affect_color, float coat_affect_roughness, float thin_film_thickness, float thin_film_IOR, bool thin_walled, vec3 normal, vec3 tangent, inout BSDF bsdf)
{
	// 
	// Coat affect roughness: blend specular roughness toward 1.0
	float coat_roughness_factor = (coat_affect_roughness * coat) * coat_roughness;
	float coat_affected_specular_roughness = (specular_roughness * (1 - coat_roughness_factor)) + coat_roughness_factor;
	// 
	// Roughness
	vec2 main_roughness;
	mx_roughness_anisotropy(coat_affected_specular_roughness, specular_anisotropy, main_roughness);
	// 
	// Tangent rotation
	vec3 main_tangent = tangent;
	if (specular_anisotropy > 0.0)
	{
		float tangent_rotate_degree = specular_rotation * 360.0;
		vec3 tangent_rotated;
		mx_rotate_vector3(tangent, tangent_rotate_degree, normal, tangent_rotated);
		main_tangent = normalize(tangent_rotated);
	}
	// 
	// Coat tangent rotation
	vec3 coat_tangent = tangent;
	if (coat_anisotropy > 0.0)
	{
		float coat_tangent_rotate_degree = coat_rotation * 360.0;
		vec3 coat_tangent_rotated;
		mx_rotate_vector3(tangent, coat_tangent_rotate_degree, coat_normal, coat_tangent_rotated);
		coat_tangent = normalize(coat_tangent_rotated);
	}
	// 
	// Coat affect color: darken diffuse under the coat
	vec3 coat_gamma = vec3((clamp(coat, 0.0, 1.0) * coat_affect_color) + 1.0);
	vec3 coat_affected_diffuse_color = pow(clamp(base_color, 0.0, 1.0), coat_gamma);
	// 
	// Coat affect subsurface color
	vec3 coat_affected_subsurface_color = pow(clamp(subsurface_color, 0.0, 1.0), coat_gamma);
	// 
	// Diffuse BSDF (Oren-Nayar)
	BSDF diffuse_bsdf;
	diffuse_bsdf.response = vec3(0.0, 0.0, 0.0);
	diffuse_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_oren_nayar_diffuse_bsdf(closureData, base, coat_affected_diffuse_color, diffuse_roughness, normal, true, diffuse_bsdf);
	// 
	// Subsurface scattering
	vec3 subsurface_radius_scaled = subsurface_radius * subsurface_scale;
	BSDF sss_bsdf;
	sss_bsdf.response = vec3(0.0, 0.0, 0.0);
	sss_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	if (thin_walled)
	{
		mx_translucent_bsdf(closureData, 1.0, coat_affected_subsurface_color, normal, sss_bsdf);
	}
	else
	{
		mx_subsurface_bsdf(closureData, 1.0, coat_affected_subsurface_color, subsurface_radius_scaled, subsurface_anisotropy, normal, sss_bsdf);
	}
	// 
	// Subsurface mix: blend SSS with diffuse
	BSDF subsurface_mix;
	subsurface_mix.response = mix(diffuse_bsdf.response, sss_bsdf.response, subsurface);
	subsurface_mix.throughput = mix(diffuse_bsdf.throughput, sss_bsdf.throughput, subsurface);
	// 
	// Sheen BSDF
	BSDF sheen_bsdf_out;
	sheen_bsdf_out.response = vec3(0.0, 0.0, 0.0);
	sheen_bsdf_out.throughput = vec3(1.0, 1.0, 1.0);
	mx_sheen_bsdf(closureData, sheen, sheen_color, sheen_roughness, normal, 0, sheen_bsdf_out);
	// 
	// Sheen layer: sheen over subsurface mix
	bsdf.response = sheen_bsdf_out.response + (subsurface_mix.response * sheen_bsdf_out.throughput);
	bsdf.throughput = sheen_bsdf_out.throughput * subsurface_mix.throughput;
	// 
	// Transmission roughness (coat-affected)
	float transmission_roughness_clamped = clamp(specular_roughness + transmission_extra_roughness, 0.0, 1.0);
	float transmission_roughness_scalar = (transmission_roughness_clamped * (1 - coat_roughness_factor)) + coat_roughness_factor;
	vec2 transmission_roughness;
	mx_roughness_anisotropy(transmission_roughness_scalar, specular_anisotropy, transmission_roughness);
	// 
	// Transmission BSDF (dielectric transmission)
	BSDF transmission_bsdf;
	transmission_bsdf.response = vec3(0.0, 0.0, 0.0);
	transmission_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_dielectric_bsdf(closureData, 1.0, transmission_color, specular_IOR, transmission_roughness, false, 0.0, 1.5, normal, main_tangent, 0, 1, transmission_bsdf);
	// 
	// Transmission mix: blend transmission with sheen layer
	bsdf.response = mix(bsdf.response, transmission_bsdf.response, transmission);
	bsdf.throughput = mix(bsdf.throughput, transmission_bsdf.throughput, transmission);
	// 
	// Specular BSDF (dielectric reflection)
	BSDF specular_bsdf;
	specular_bsdf.response = vec3(0.0, 0.0, 0.0);
	specular_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_dielectric_bsdf(closureData, specular, specular_color, specular_IOR, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, main_tangent, 0, 0, specular_bsdf);
	// 
	// Layer: specular over transmission mix
	bsdf.response = specular_bsdf.response + (bsdf.response * specular_bsdf.throughput);
	bsdf.throughput = specular_bsdf.throughput * bsdf.throughput;
	// 
	// Artistic IOR (reflectivity/edge-color -> physical IOR/extinction)
	vec3 metal_reflectivity = base_color * base;
	vec3 metal_edgecolor = specular_color * specular;
	vec3 ior_n;
	vec3 ior_k;
	mx_artistic_ior(metal_reflectivity, metal_edgecolor, ior_n, ior_k);
	// 
	// Conductor BSDF (metal reflection)
	BSDF metal_bsdf;
	metal_bsdf.response = vec3(0.0, 0.0, 0.0);
	metal_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_conductor_bsdf(closureData, metalness, ior_n, ior_k, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, main_tangent, 0, metal_bsdf);
	// 
	// Metalness mix: conductor (fg) vs specular layer (bg)
	// Conductor response is already scaled by metalness (the weight),
	// so we just add it to the attenuated specular layer.
	float one_minus_metalness = 1 - metalness;
	bsdf.response = metal_bsdf.response + (bsdf.response * one_minus_metalness);
	bsdf.throughput = metal_bsdf.throughput + (bsdf.throughput * one_minus_metalness);
	// 
	// Coat attenuation: tint underlying layers by coat color
	// Float3 coercion needed: RgbF lerp result -> Float3 for BSDF multiply
	vec3 coat_attenuation = mix(vec3(1.0), coat_color, coat);
	bsdf.response = bsdf.response * coat_attenuation;
	bsdf.throughput = bsdf.throughput * coat_attenuation;
	// 
	// Coat roughness
	vec2 coat_roughness_vec;
	mx_roughness_anisotropy(coat_roughness, coat_anisotropy, coat_roughness_vec);
	// 
	// Coat BSDF (dielectric reflection)
	BSDF coat_bsdf;
	coat_bsdf.response = vec3(0.0, 0.0, 0.0);
	coat_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_dielectric_bsdf(closureData, coat, vec3(1.0, 1.0, 1.0), coat_IOR, coat_roughness_vec, false, 0.0, 1.5, coat_normal, coat_tangent, 0, 0, coat_bsdf);
	// 
	// Coat layer: coat over attenuated base
	bsdf.response = coat_bsdf.response + (bsdf.response * coat_bsdf.throughput);
	bsdf.throughput = coat_bsdf.throughput * bsdf.throughput;
}

