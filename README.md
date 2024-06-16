# Metashade
## What is Metashade?
Metashade is an experimental GPU shading domain-specific language (DSL) embedded in Python.
When a Metashade script executes, it generates code in a target shading language.
Only HLSL is supported so far but the intent is definitely to support multiple targets.

To see Metashade in action, check out the [glTF demo](gltfdemo) or the [tests](tests) which are run by CI:
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

## How does it work?
Unlike some other Python DSLs, Metashade doesn't rely on introspection to translate the Python AST to the target language.
It uses more straight-forward mechanisms in hopes of making the DSL appear less magical to the user and enabling integration with other Python code.

### Creating a generator

Before Metashade can generate anything, a generator object has to be created for a specific target shading
language profile, with an output file (or a file-like stream object) passed as a constructor argument, e.g.

```Python
from metashade.hlsl.sm6 import ps_6_0

with open("ps.hlsl", 'w') as ps_file:
    sh = ps_6_0.Generator(ps_file)
```

Note that, by convention, the generator object is always named `sh` (for "shader").
This helps Metashade code be polymorphic with regard to different target profiles.
E.g. code with the same logic can be generated for an HLSL pixel shader and a GLSL compute shader.

### Function definitions

Metashade function definition syntax looks like this:

```Python
with sh.function('add', sh.Float4)(a = sh.Float4, b = sh.Float4):
    sh.return_(sh.a + sh.b)
```

Here, the first pair of parentheses defines the function name and the return type,
while the second pair contains parameter declarations with their types.
All data types here can be determined dynamically at generation time and become static in the generated code.

The above Python code generates the following HLSL:

```HLSL
float4 add(float4 a, float4 b)
{
	return (a + b);
}
```

### Entry points

Shader entry points are really just a special case of functions in Metashade, for example:

```Python
with sh.ps_output('PsOut') as PsOut:
    PsOut.SV_Target('color', sh.RgbaF)

with sh.main('mainPS', sh.PsOut)():
    sh.psOut = sh.PsOut()
    sh.psOut.color.rgb = sh.RgbF(1)
    sh.psOut.color.a = 1
    sh.return_(sh.psOut)
```

Which generates in HLSL:

```HLSL
struct PsOut
{
	float4 color : SV_TARGET;
};

PsOut mainPS()
{
	PsOut psOut;
	psOut.color.rgb = 1.0.xxx;
	psOut.color.a = 1.0;
	return psOut;
}
```

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

