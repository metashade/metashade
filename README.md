# Metashade
## What is Metashade?
Metashade is an experimental GPU shading domain-specific language (DSL) embedded in Python.
When a Metashade script executes, it generates code in a target shading language.
Only HLSL is supported so far but the intent is definitely to support multiple targets.

To see Metashade in action, check out the glTF demo at https://github.com/ppenenko/metashade-glTFSample or the [tests](tests) which are run by CI:
[![GitHub Actions CI](https://github.com/ppenenko/metashade/actions/workflows/python-package.yml/badge.svg)](https://github.com/ppenenko/metashade/actions/workflows/python-package.yml)

For a detailed discussion of the motivation for Metashade and its design, please see the [presentation on Google Slides](https://docs.google.com/presentation/d/e/2PACX-1vQtYIwXIkMnVC6TzWTKPAtZIA6_xeUCQc8Mvyziu0qy7HDUduz_onsJ5TabxTuuVQ/pub?start=false&loop=false&delayms=3000).

## Rationale

* Programming at a more abstract level than the target language:
    * Metaprogramming - think C++ templates but with greater flexibility.
    Like any other Python code, Mestashade code is polymorphic at generation time.
    This approach can replace the traditional ubershader practice, effectively replacing the C preprocessor with Python.
    * Stricter typing - e.g. a 3D point and an RGB color can be represented with different Metashade types, backed by the same data type in HLSL.
* Multi-language/cross-platform support.
    Cross-compilation (e.g. with SPIRV-Cross) is definitely an alternative but the code generation approach should offer higher flexibility around:
    * more divergent languages, e.g. HLSL vs OSL;
    * language dialects;
    * integration required by the specific host application (a shader fragment with an interface defined in metadata, an effect file etc.),
    which is hard to accomplish with cross-compilation because it typically operates on final,
    full shaders with a defined entry point.
* Easy integration with content pipeline and build system scripts written in Python, and the vast Python ecosystem in general.

## What does it look like?

The following Metashade Python code

```Python
with sh.function('D_Ggx', sh.Float)(                # <-- The function name and return type
    NdotH = sh.Float, fAlphaRoughness = sh.Float    # <-- The function parameters
):
    # Initializing some locals
    sh.fASqr = sh.fAlphaRoughness * sh.fAlphaRoughness
    sh.fF = (sh.NdotH * sh.fASqr - sh.NdotH) * sh.NdotH + sh.Float(1.0)

    # Generating the return statement in the target language
    sh.return_(
        (sh.fASqr / (sh.Float(math.pi) * sh.fF * sh.fF )).saturate()
    )
```

generates the following HLSL output:

```C
float D_Ggx(float NdotH, float fAlphaRoughness)
{
    float fASqr = (fAlphaRoughness * fAlphaRoughness);
    float fF = ((((NdotH * fASqr) - NdotH) * NdotH) + 1.0);
    return saturate((fASqr / ((3.141592653589793 * fF) * fF)));
}
```

## How does it work?

Popular Pythonic GPU DSLs like [Nvidia Warp](https://github.com/NVIDIA/warp),
[Taichi](https://github.com/taichi-dev/taichi),
[Numba](https://github.com/numba/numba)
and [OpenAI’s Triton](https://github.com/openai/triton)
rely on Python's introspection to capture the Python AST and transpile it to the target language.
This approach can only support a subset of Python syntax that maps onto the target language.

In contrast, Metashade generates target code dynamically, during the execution of Python code,
modeling the state of the shader being generated in objects called generators.
This requires some idiosyncratic Python syntax but in return we get the full power of Python at generation time.
Python's run time becomes the shader's design time, and it becomes a metaprogramming language, replacing mechanisms like the C Preprocessor, generics and templates.

This offers the following benefits:
* Easy-to-use metaprogramming. Imperative metaprogramming is possible (C++ templates are a pure-functional language).
* The whole stack is debuggable by the application programmer.
* Codegen can interact with the outside world (file system or user input). E.g. the [glTF demo](https://github.com/ppenenko/metashade-glTFSample) loads glTF assets and generates shaders based on their contents.
* Codegen can integrate with arbitrary Python code. E.g. the [glTF demo](https://github.com/ppenenko/metashade-glTFSample) the third-party [pygltflib](https://pypi.org/project/pygltflib/) to parse glTF assets.
* It's easy to build abstractions on top of basic codegen.

### Creating a generator

Before Metashade can generate anything, a generator object has to be created for a specific target shading
language profile, with an output file (or a file-like stream object) passed as a constructor argument, e.g.

```Python
from metashade.hlsl.sm6 import ps_6_0 as hlsl_ps
from metashade.glsl.v460 import frag as glsl_fs # hypothetical

def generate(sh):
    # Polymorphic shader code for multiple targets
    pass

with open('ps.hlsl', 'w') as hlsl_file:
    sh = hlsl_ps.Generator(hlsl_file)
    generate(sh)

with open('fs.glsl', 'w') as glsl_file:
    sh = glsl_fs.Generator(glsl_file)
    generate(sh)
```

Note that, by convention, the generator object is always named `sh` (for "shader").
This helps Metashade code be polymorphic with regard to different target profiles.
E.g. code with the same logic can be generated for an HLSL pixel shader and a GLSL compute shader.

### Generating C-like scopes and local variables

Metashade uses Python variables to represent variables in target C-like shading languages,
but there obviously major differences in their behavior, namely:
* Unlike in Python, lifetimes of variables in C-like languages are tied to the scope they're defined in.
* In Python, variables are always assigned by reference and the same variable can point to different objects of different types in its lifetime. Variables in C-like shading languages, in contrast,
are typed statically and are assigned by value.

Addressing these differences requires explicit emulation in Python code.
`with` scopes are the closest analogy for C-like scopes in Python,
however they only apply to the variables referenced in the `with` statement and call the special
`__enter__` and `__exit__` methods instead of construction and destruction like in C++.
That's why Metashade uses `with` statements with special objects such as function definitions created with `sh.function`,
which modify the state of the generator.
The generator emulates C-like scopes internally, and and the generated variables are modeled with member variables on the generator, which are implemented with the `__getattr__()`/`__setattr__()` Python mechanism.
With `__setattr__()` for example, we can capture the variable's name without Python introspection.
We can also easily check in `__setattr__()` if the user is trying to reinitialize the variable with a different type and we can similarly raise an exception in `__getattr__()` if the user tries to access a variable that's gone out of scope.

The `__getattr__()`/`__setattr__()` is also used for other features, such as accessing struct members and vector elements.

Further, Python expressions model expressions in the target language with help of operator overloading. Basically, `a + b` generates the respective operation in the target language instead of performing the addition in Python.

## More examples

The following Python code

```Python
sh.rgba = sh.RgbaF(rgb = (0, 1, 0), a = 0)

sh // 'Swizzling - the destination type is deduced'
sh // "a-la `auto` in C++"
sh.color = sh.rgba.rgb

sh // 'Write masking'
sh.color.r = 1

sh // 'Intrinsics example'
sh.N = sh.N.normalize()

sh // 'Dot product == Python 3 matmul'
sh // '(a.k.a. "walrus") operator'
sh.NdotL = sh.N @ sh.L

# The walrus operator is also used to
# combine textures and samplers
combined_sampler = sh.g_tColor @ sh.g_sColor

sh // 'Sample the texture'
sh.rgbaSample = combined_sampler(sh.uv)
```

generates the following HLSL:

```HLSL
float4 rgba = float4(float3(0, 1, 0), 0);

// Swizzling - the destination type is deduced
// a-la `auto` in C++
float3 color = rgba.rgb;

// Write masking
color.r = 1;

// Intrinsics example
N = normalize(N);

// Dot product == Python 3 matmul
// (a.k.a. "walrus") operator
float NdotL = dot(N, L);

// Sample the texture
float4 rgbaSample = g_tColor.Sample(g_sColor, uv);
```
