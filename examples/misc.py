
# Swizzling

sh.rgba = sh.RgbaF(rgb = (0, 1, 0), a = 0)
sh.rgb = sh.rgba.rgb    # OK, creates an `RgbF`
sh.xyz = sh.rgba.xyz    # Exception!

# Write masking

sh.rgb.r = 1

# Dot product

sh.NdotL = sh.N @ sh.L

# Intrinsics

sh.N = sh.N.normalize()