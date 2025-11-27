# Copyright 2022 Pavlo Penenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import filecmp, inspect
from pathlib import Path
import abc, io, os, sys
import pytest

from metashade.glsl import frag
from metashade.glsl.util import glslang
from metashade.hlsl.sm6 import ps_6_0
from metashade.hlsl.util import dxc

class RefDiffer:
    def __init__(self, ref_dir : Path):
        self._ref_dir = ref_dir

    def __call__(self, path : Path):
        assert filecmp.cmp(path, self._ref_dir / path.name)

def get_test_func_name():
    for frame in inspect.stack():
        if frame.function.startswith('test_'):
            return frame.function
    raise RuntimeError('No test function found in the stack')

class _TestContext(abc.ABC):
    _entry_point_name = 'main'
    _is_setup = False
    _tests_dir = None  # Will be set by conftest.py

    @classmethod
    def setup_class(cls):
        if cls._is_setup:
            return
        cls._is_setup = True
        
        # Use the directory configured by conftest.py
        if cls._tests_dir is not None:
            cls._parent_dir = cls._tests_dir
        else:
            # Fallback: Find the test file's directory from the call stack
            for frame in inspect.stack():
                if frame.filename.endswith(('test_' +  frame.filename.split('test_')[-1])) and '/tests/' in frame.filename.replace('\\', '/'):
                    cls._parent_dir = Path(frame.filename).parent
                    break
            else:
                # Final fallback
                cls._parent_dir = Path(sys.modules[cls.__module__].__file__).parent

        out_dir = os.getenv('METASHADE_PYTEST_OUT_DIR', None)
        ref_dir = cls._parent_dir / 'ref'

        if out_dir is None:
            # Don't compare against references explicitly in the script.
            # Instead, overwrite the references with the generated files.
            # This is useful for diffing or updating the references manually with
            # git.
            cls._out_dir = ref_dir
            cls._ref_differ = None
        else:
            cls._out_dir = Path(out_dir).resolve()
            cls._ref_differ = RefDiffer(ref_dir)

        os.makedirs(cls._out_dir, exist_ok = True)

    def __init__(
        self,
        no_file : bool = False,
        as_lib : bool = False,
        dummy_entry_point : bool = False
    ):
        # Ensure setup_class has been called
        if not self.__class__._is_setup:
            self.__class__.setup_class()
            
        test_name = get_test_func_name()
        self._src_path = (
            None if no_file
            else self._out_dir / f'{test_name}.{self._file_extension}'
        )
        self._as_lib = as_lib
        self._dummy_entry_point = dummy_entry_point

    @abc.abstractmethod
    def _create_generator(self):
        pass

    def _check_source(self):
        if self._src_path is None:
            return

        if self._ref_differ is not None:
            self._ref_differ(self._src_path)
        self._compile()
    
    @abc.abstractmethod
    def _compile(self):
        pass

    def __enter__(self):
        self._file = (
            open(self._src_path, 'w') if self._src_path is not None
            else io.StringIO()
        )
        self._sh = self._create_generator()
        return self._sh

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._file.close()
            return False
        if self._dummy_entry_point:
            with self._sh.entry_point(self._entry_point_name)():
                pass
        self._file.close()
        self._check_source()
        return True

class HlslTestContext(_TestContext):
    _file_extension = 'hlsl'

    def _create_generator(self):
        return ps_6_0.Generator(self._file)

    def _compile(self):
        def dxc_compile(profile, to_spirv):
            dxc.compile(
                src_path = self._src_path,
                entry_point_name = self._entry_point_name,
                profile = profile,
                include_paths = [ self._parent_dir ],
                to_spirv = to_spirv
            )

        # LIB profiles support DXIL linking and therefore allow function
        # declarations without definitions.
        # Pure declarations may also be useful in other profiles if the
        # definition is found elsewhere in the compilation unit, e.g. in an
        # included header.
        dxc_compile(
            profile = 'lib_6_5' if self._as_lib else 'ps_6_0',
            to_spirv = False
        )

        if not self._as_lib:
            dxc_compile(
                profile = 'ps_6_0',
                to_spirv = True
            )

class GlslTestContext(_TestContext):
    _file_extension = 'glsl'
    
    def _create_generator(self):
        return frag.Generator(self._file, '450')

    def _compile(self):
        glslang.compile(
            src_path = self._src_path,
            target_env = 'vulkan1.1',
            shader_stage = 'frag',
            output_path = os.devnull
        )

def ctx_cls_hg(func):
    wrapped_deco = pytest.mark.parametrize(
        'ctx_cls', [HlslTestContext, GlslTestContext]
    )
    return wrapped_deco(func)
