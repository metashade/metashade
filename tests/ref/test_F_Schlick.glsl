#version 450
// Schlick's approximation of the Fresnel term.
// 
// Args:
// LdotH: Dot product of light direction and half-vector
// rgbF0: Reflectance at normal incidence
// 
// Returns:
// Fresnel reflectance
//
vec3 F_Schlick(float LdotH, vec3 rgbF0)
{
	return rgbF0 + ((vec3(1.0) - rgbF0) * pow(1.0 - LdotH, 5.0));
}

void main()
{
}

