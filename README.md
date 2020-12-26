# Metashade
## What is Metashade?
Metashade is an experimental GPU shading domain-specific language (DSL) embedded in Python.
When a Metashade script executes, it generates code in a target shading language (HLSL only so far but the intent is definitely to support multiple targets).
You can refer to [test_fx.py](tests/test_fx.py) as a "Hello World" example.

## Why Metashade?
* Programming at a more abstract level than the target language:
    * Metaprogramming - think C++ templates but more flexible.
Replacing the ubershader approach, i.e. replacing the C preprocessor with Python.
    * Stricter typing - think a 3D point vs an RGB color, represented with the same data type in HLSL.
* Multi-language/cross-platform support.
Cross-compilation (e.g. with SPIRV-Cross) is an alternative but the code generation approach should offer higher flexibility around:
    * more divergent languages, e.g. HLSL vs OSL;
    * language dialects;
    * integration required by the specific host application (a shader fragment with a known interface, an effect file etc.).
* Integration with content pipeline scripts written in Python.

## How does it work?
Unlike some other Python DSLs, Metashade doesn't rely on introspection to translate the Python AST to the target language.
It uses more straight-forward mechanisms in hopes of making the DSL appear less magical to the user:

* Operator overloading. Basically, `a + b` generates the respective operation in the target language instead of performing the addition in Python.
* Representing scopes in the target C-like language with `with` scopes in Python.
* `__getattr__()` and `__setattr__()` are used to initialize, modify and reference target variables in the current scope.
* C-like assignment by value is represented with assigment to a special data member `_`.