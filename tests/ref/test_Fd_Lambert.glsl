#version 450
// Lambertian diffuse BRDF.
// 
// Returns the constant 1/\u03c0 factor for energy-conserving Lambertian diffuse.
// Multiply by the diffuse albedo to get the full diffuse contribution.
// 
// Returns:
// 1/\u03c0 (the Lambertian BRDF normalization factor)
// 
// Reference:
// https://google.github.io/filament/Filament.md.html#materialsystem/diffusebrdf
//
#line 27 "/app/tests/test_std_diffuse.py"
float Fd_Lambert()
{
	return 0.3183098861837907;
}

#line 26 "/app/tests/test_std_diffuse.py"
void main()
{
}

