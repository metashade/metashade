// GGX/Trowbridge-Reitz Normal Distribution Function.
// 
// Args:
// NdotH: Dot product of surface normal and half-vector
// fAlphaRoughness: Roughness parameter (perceptualRoughness^2)
// 
// Returns:
// NDF value
//
float D_Ggx(float NdotH, float fAlphaRoughness)
{
	// https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/normaldistributionfunction(speculard)
	// 
	float fASqr = fAlphaRoughness * fAlphaRoughness;
	float fF = (((NdotH * fASqr) - NdotH) * NdotH) + 1.0;
	return saturate(fASqr / ((3.141592653589793 * fF) * fF));
}

void main()
{
}

