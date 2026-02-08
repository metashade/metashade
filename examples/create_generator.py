from metashade.targets.hlsl.sm6 import ps_6_0
from metashade.targets.glsl import frag

def generate(sh):
    # Polymorphic shader code for multiple targets
    pass

with open('ps.hlsl', 'w') as ps_file:
    sh = ps_6_0.Generator(ps_file)
    generate(sh)

with open('fs.glsl', 'w') as frag_file:
    sh = frag.Generator(frag_file)
    generate(sh)
