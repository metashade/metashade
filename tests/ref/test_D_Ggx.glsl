#version 450
float D_Ggx(float NdotH, float fAlphaRoughness)
{
	// https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/normaldistributionfunction(speculard)
	// 
	float fASqr = fAlphaRoughness * fAlphaRoughness;
	float fF = (((NdotH * fASqr) - NdotH) * NdotH) + 1.0;
	return clamp(fASqr / ((3.141592653589793 * fF) * fF), 0.0, 1.0);
}

void main()
{
}

