float3 F_Schlick(float LdotH, float3 rgbF0)
{
	return rgbF0 + ((1.0.xxx - rgbF0) * pow(1.0 - LdotH, 5.0));
}

void main()
{
}

