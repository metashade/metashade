#include "mx_roughness_anisotropy.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_dielectric_bsdf.glsl"
#include "mx_conductor_bsdf.glsl"
#include "mx_artistic_ior.glsl"
void mx_metashade_standard_surface_bsdf(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float metalness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float thin_film_thickness, float thin_film_IOR, vec3 normal, vec3 tangent, inout BSDF bsdf)
{
	// 
	// Roughness
	vec2 main_roughness;
	mx_roughness_anisotropy(specular_roughness, specular_anisotropy, main_roughness);
	// 
	// Diffuse BSDF (Oren-Nayar)
	BSDF diffuse_bsdf;
	diffuse_bsdf.response = vec3(0.0, 0.0, 0.0);
	diffuse_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_oren_nayar_diffuse_bsdf(closureData, base, base_color, diffuse_roughness, normal, true, diffuse_bsdf);
	// 
	// Specular BSDF (dielectric reflection)
	BSDF specular_bsdf;
	specular_bsdf.response = vec3(0.0, 0.0, 0.0);
	specular_bsdf.throughput = vec3(1.0, 1.0, 1.0);
	mx_dielectric_bsdf(closureData, specular, specular_color, specular_IOR, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, tangent, 0, 0, specular_bsdf);
	// 
	// Layer: specular over diffuse
	bsdf.response = specular_bsdf.response + (diffuse_bsdf.response * specular_bsdf.throughput);
	bsdf.throughput = specular_bsdf.throughput * diffuse_bsdf.throughput;
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
	mx_conductor_bsdf(closureData, metalness, ior_n, ior_k, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, tangent, 0, metal_bsdf);
	// 
	// Metalness mix: conductor (fg) vs specular+diffuse (bg)
	// Conductor response is already scaled by metalness (the weight),
	// so we just add it to the attenuated dielectric+diffuse stack.
	float one_minus_metalness = 1 - metalness;
	bsdf.response = metal_bsdf.response + (bsdf.response * one_minus_metalness);
	bsdf.throughput = metal_bsdf.throughput + (bsdf.throughput * one_minus_metalness);
}

