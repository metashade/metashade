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

import abc
import filecmp, io, os, sys
from pathlib import Path
from metashade.hlsl.util import dxc
from metashade.util.tests import RefDiffer

class _TestContext(abc.ABC):
    @classmethod
    def _check_source(cls, hlsl_path, as_lib : bool = False):
        pass

    def _create_generator(self, hlsl_path : str, as_lib : bool = False):
        return self._generator_cls(hlsl_path, as_lib)
    
    @abc.abstractmethod
    def _compile(self, hlsl_path : str, as_lib : bool = False):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return False
        self._check_source(self._hlsl_path, self._as_lib)
        return True

class HlslTestContext(_TestContext):
    _file_extension = 'hlsl'
    
    @classmethod
    def _check_source(cls, hlsl_path, as_lib : bool = False):
        pass

    def _compile(self, hlsl_path : str, as_lib : bool = False):
        # LIB profiles support DXIL linking and therefore allow function
        # declarations without definitions.
        # Pure declarations may also be useful in other profiles if the
        # definition is found elsewhere in the compilation unit, e.g. in an
        # included header.
        dxc.compile(
            src_path = hlsl_path,
            entry_point_name = cls._entry_point_name,
            profile = 'lib_6_5' if as_lib else 'ps_6_0',
            include_paths = [ cls._parent_dir ]
        )

class TestBase:
    @classmethod
    def setup_class(cls):
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

    _entry_point_name = 'psMain'

    @classmethod
    def _get_out_path(cls, file_name : str, file_extension : str) -> str:
        return ( cls._out_dir / f'{file_name}.{file_extension}'
            if file_name is not None else None
        )

    @classmethod
    def _get_hlsl_path(cls, file_name : str) -> str:
        return cls._get_out_path(file_name, 'hlsl')
    
    @classmethod
    def _get_glsl_path(cls, file_name : str) -> str:
        return cls._get_out_path(file_name, 'glsl')

    @staticmethod
    def _open_file(hlsl_path : str = None):
        return ( open(hlsl_path, 'w')
            if hlsl_path is not None else io.StringIO()
        )

    @classmethod
    def _check_source(cls, hlsl_path, as_lib : bool = False):
        if cls._ref_differ is not None:
            cls._ref_differ(hlsl_path)

        # LIB profiles support DXIL linking and therefore allow function
        # declarations without definitions.
        # Pure declarations may also be useful in other profiles if the
        # definition is found elsewhere in the compilation unit, e.g. in an
        # included header.
        dxc.compile(
            src_path = hlsl_path,
            entry_point_name = cls._entry_point_name,
            profile = 'lib_6_5' if as_lib else 'ps_6_0',
            include_paths = [ cls._parent_dir ]
        )
