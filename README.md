# Metashade
## What is Metashade?
Metashade is an experimental GPU shading DSL embedded in Python.
When a Metashade script executes, it generates code in a target shading language (only HLSL is supported at the moment but the intent is definitely to support multiple targets).
You can refer to [test_fx.py](tests/test_fx.py) as a "Hello World" example.

## Why Metashade?
### Cross-platform support
Being able to generate code in multiple target languages from the same Metashade script is a key goal of the project. The following languages look like attractive targets:
* HLSL - the only currently supported target.
* GLSL
* OSL
* OpenCL
* CUDA

Admittedly, the modern open-source ecosystem that has evolved around SPIR-V has solved many of the cross-platform shading concerns with cross-compilation, however code generation offers a few key benefits:
* SPIR-V is designed to represent complete shader stages, ready to be sent to the GPU.
Specific apps on the other hand
    * Preprocessor definitions
    * Fragments
    * Effect files.
* SPIR-V wasn't designed with production shading languages like OSL in mind.

It doesn't support 
* There is really not just one standard HLSL or GLSL target. A specific app would



    * More readable
* Final shader stage.
* Preprocessor not supported
* Generic, abstract programming
* Stricter type safety
* OSL
* Python excels as a glue language, so Metashade-based scripts can be tightly integrated into content pipelines using Python.

## How is it different from other shading DSLs written in Python?
There have definitely been earlier attempts at shader generation with Python.

## How does it work?
* Generator
* Operator overloading
* __setattr__()
* `with` scopes
* Assignment by value