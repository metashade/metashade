#include "mx_roughness_anisotropy.glsl"
#include "mx_rotate_vector3.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_dielectric_bsdf.glsl"
#include "mx_conductor_bsdf.glsl"
#include "mx_artistic_ior.glsl"
void mx_metashade_standard_surface_bsdf(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float metalness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float specular_rotation, float transmission, vec3 transmission_color, float transmission_extra_roughness, float thin_film_thickness, float thin_film_IOR, vec3 normal, vec3 tangent, inout BSDF bsdf)
{
	// 
	// Roughness
	vec2 main_roughness;
	mx_roughness_anisotropy(specular_roughness, specular_anisotropy, main_roughness);
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
	// Diffuse BSDF (Oren-Nayar)
	BSDF diffuse_bsdf;
	diffuse_bsdf.response = vec3(0.0, 0.0, 0.0);
	diffuse_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_oren_nayar_diffuse_bsdf(closureData, base, base_color, diffuse_roughness, normal, true, diffuse_bsdf);
	// 
	// Transmission roughness
	float transmission_roughness_scalar = clamp(specular_roughness + transmission_extra_roughness, 0.0, 1.0);
	vec2 transmission_roughness;
	mx_roughness_anisotropy(transmission_roughness_scalar, specular_anisotropy, transmission_roughness);
	// 
	// Transmission BSDF (dielectric transmission)
	BSDF transmission_bsdf;
	transmission_bsdf.response = vec3(0.0, 0.0, 0.0);
	transmission_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_dielectric_bsdf(closureData, 1.0, transmission_color, specular_IOR, transmission_roughness, false, 0.0, 1.5, normal, main_tangent, 0, 1, transmission_bsdf);
	// 
	// Transmission mix: blend transmission with diffuse
	float one_minus_transmission = 1 - transmission;
	bsdf.response = (transmission_bsdf.response * transmission) + (diffuse_bsdf.response * one_minus_transmission);
	bsdf.throughput = (transmission_bsdf.throughput * transmission) + (diffuse_bsdf.throughput * one_minus_transmission);
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
}

