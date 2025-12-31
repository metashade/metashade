float V_SmithGgxCorrelated(float NdotV, float NdotL, float fAlphaRoughness)
{
	// https://google.github.io/filament/Filament.md.html#materialsystem/specularbrdf/geometricshadowing(specularg)
	// 
	float fASqr = fAlphaRoughness * fAlphaRoughness;
	float fGgxL = NdotV * sqrt(((NdotL - (NdotL * fASqr)) * NdotL) + fASqr);
	float fGgxV = NdotL * sqrt(((NdotV - (NdotV * fASqr)) * NdotV) + fASqr);
	float fV = 0.5 / (fGgxL + fGgxV);
	return saturate(fV);
}

void main()
{
}

