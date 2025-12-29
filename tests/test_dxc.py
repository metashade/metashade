# Copyright 2023 Pavlo Penenko
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

import pathlib, pytest, sys
from subprocess import CalledProcessError
from metashade.hlsl.util import dxc

class TestDxc:
    def test_dxc_failure(self):
        parent_dir = pathlib.Path(sys.modules[self.__module__].__file__).parent
        try:
            with pytest.raises(CalledProcessError):
                dxc.compile(
                    src_path = parent_dir / 'fail.hlsl',
                    profile = 'lib_6_5',
                )
        except FileNotFoundError as e:
            pytest.skip(f"dxc not found: {e}")
