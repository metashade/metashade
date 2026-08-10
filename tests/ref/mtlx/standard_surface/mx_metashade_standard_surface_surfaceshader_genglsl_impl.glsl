#include "mx_roughness_anisotropy.glsl"
#include "mx_oren_nayar_diffuse_bsdf.glsl"
#include "mx_dielectric_bsdf.glsl"
void mx_metashade_standard_surface_surfaceshader(ClosureData closureData, float base, vec3 base_color, float diffuse_roughness, float metalness, float specular, vec3 specular_color, float specular_roughness, float specular_IOR, float specular_anisotropy, float specular_rotation, float transmission, vec3 transmission_color, float transmission_depth, vec3 transmission_scatter, float transmission_scatter_anisotropy, float transmission_dispersion, float transmission_extra_roughness, float subsurface, vec3 subsurface_color, vec3 subsurface_radius, float subsurface_scale, float subsurface_anisotropy, float sheen, vec3 sheen_color, float sheen_roughness, float coat, vec3 coat_color, float coat_roughness, float coat_anisotropy, float coat_rotation, float coat_IOR, vec3 coat_normal, float coat_affect_color, float coat_affect_roughness, float thin_film_thickness, float thin_film_IOR, float emission, vec3 emission_color, vec3 opacity, bool thin_walled, vec3 normal, vec3 tangent, out surfaceshader out_)
{
	vec2 main_roughness;
	mx_roughness_anisotropy(specular_roughness, specular_anisotropy, main_roughness);
	BSDF diffuse_bsdf;
	mx_oren_nayar_diffuse_bsdf(closureData, base, base_color, diffuse_roughness, normal, true, diffuse_bsdf);
	BSDF specular_bsdf;
	mx_dielectric_bsdf(closureData, specular, specular_color, specular_IOR, main_roughness, false, thin_film_thickness, thin_film_IOR, normal, tangent, 0, 0, specular_bsdf);
	out_.color = specular_bsdf.response + (diffuse_bsdf.response * specular_bsdf.throughput);
	out_.transparency = vec3(0.0, 0.0, 0.0);
}

