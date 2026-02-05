#version 450
// Smith-GGX Height-Correlated Visibility Function.
// 
// This is the visibility term, combining
// the geometric shadowing and masking into a single optimized form.
// 
// Args:
// NdotV: Dot product of surface normal and view direction
// NdotL: Dot product of surface normal and light direction
// fAlphaRoughness: Roughness parameter (perceptualRoughness^2)
// 
// Returns:
// Visibility term value
//
#line 36 "/app/tests/test_std_microfacet.py"
float V_SmithGgxCorrelated(float NdotV, float NdotL, float fAlphaRoughness)
{
	// https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/geometricshadowing(specularg)
	// 
	float fASqr = fAlphaRoughness * fAlphaRoughness;
	float fGgxL = NdotV * sqrt(((NdotL - (NdotL * fASqr)) * NdotL) + fASqr);
	float fGgxV = NdotL * sqrt(((NdotV - (NdotV * fASqr)) * NdotV) + fASqr);
	float fV = 0.5 / (fGgxL + fGgxV);
	return clamp(fV, 0.0, 1.0);
}

#line 35 "/app/tests/test_std_microfacet.py"
void main()
{
}

