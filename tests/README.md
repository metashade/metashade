Our test cases follow the [pytest](https://pytest.org/) conventions.
Visual Studio Code sets up a pytest integration automagically.
The tests also run as part of [GitHub Actions CI](https://github.com/metashade/metashade/actions):
[![GitHub Actions CI](https://github.com/metashade/metashade/actions/workflows/python-package.yml/badge.svg)](https://github.com/metashade/metashade/actions/workflows/python-package.yml)

Both HLSL (Shader Model 6.0) and GLSL (Vulkan 1.1 / SPIR-V) generators are tested. The automated tests don't involve any actual rendering yet, but rendering can be tested manually in the [glTF demo](https://github.com/metashade/metashade-glTFSample).

# Testing error handling

Some of the test cases cover situations where the Metashade framework is supposed to gracefully handle logical errors in user scripts. Ideally, all such errors must be handled at generation time by raising Python exceptions, as opposed to compilation time. I.e. any shaders generated with Metashade without exceptions should compile.

For such test cases, the [pytest.raises](https://docs.pytest.org/en/stable/reference/reference.html?highlight=raises#pytest.raises) pattern is used and no output shader file is generated.

# Testing successful shader generation

Other tests are supposed to generate valid shaders. For these, we verify correctness with the following checks:
* The script has executed without raising Python exceptions.
* The output shader file doesn't differ from its reference (more details below).
* The output shader file compiles successfully:
  * **HLSL**: [DXC](https://github.com/microsoft/DirectXShaderCompiler) (`dxc` must be in `PATH`)
  * **GLSL**: [glslang](https://github.com/KhronosGroup/glslang) (`glslangValidator` must be in `PATH`)

## Comparing the generated files against references

The reference shader files can be found in the [ref](ref) directory.
By default, the tests generate their outputs in the same directory, overwriting the references.
This is convenient for running the tests locally and manually reviewing the possible changes in the generated output with `git diff`.
If a change appears to be non-breaking, purely cosmetic, then the new version can be "blessed" and committed to git.

Alternatively, if the environment variable `METASHADE_PYTEST_OUT_DIR` is set, then the outputs will be generated in that directory and the test scripts will compare them to the references without involving git.
This setup is used in the CI tests.
