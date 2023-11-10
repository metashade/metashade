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

import io, os, pathlib, sys
from metashade.hlsl.common import compile

class Base:
    @classmethod
    def setup_class(cls):
        parent_dir = pathlib.Path(sys.modules[cls.__module__].__file__).parent
        cls._out_dir = os.path.join(parent_dir, 'out')
        os.makedirs(cls._out_dir, exist_ok = True)

    _entry_point_name = 'psMain'

    def _get_hlsl_path(self, file_name : str) -> str:
        return ( os.path.join(self._out_dir, f'{file_name}.hlsl')
            if file_name is not None else None
        )

    def _open_file(self, hlsl_path : str = None):
        return ( open(hlsl_path, 'w')
            if hlsl_path is not None else io.StringIO()
        )

    def _compile(self, hlsl_path, include_path = None, as_lib : bool = False):
        # LIB profiles support DXIL linking and therefore allow function
        # declarations without definitions.
        # Pure declarations may also be useful in other profiles if the
        # definition is found elsewhere in the compilation unit, e.g. in an
        # included header.
        assert 0 == compile(
            src_path = hlsl_path,
            entry_point_name = self._entry_point_name,
            profile = 'lib_6_5' if as_lib else 'ps_6_0',
            include_paths = [
                pathlib.Path(sys.modules[self.__module__].__file__).parent
            ]
        ).returncode