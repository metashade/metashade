# Copyright 2024 Pavlo Penenko
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

import filecmp, os
from pathlib import Path

class RefDiffer:
    def __init__(self, ref_dir : Path, out_dir_env_var : str):
        self._ref_dir = ref_dir

    def __call__(self, path : Path):
        assert filecmp.cmp(path, self._ref_dir / path.name)
