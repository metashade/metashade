# Copyright 2025 Pavlo Penenko
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

import os
from pathlib import Path

from metashade.util.testing import get_test_func_name, RefDiffer
from metashade.mtlx.generate import GlslGeneratorContext

class GlslTestContext(GlslGeneratorContext):
    @classmethod
    def setup_class(cls, test_dir: Path):
        cls._parent_dir = test_dir
        
        # Consistent with metashade.util.testing
        out_dir = os.getenv('METASHADE_PYTEST_OUT_DIR', None)
        # Assuming tests are in tests/mtlx, refs are in tests/ref/mtlx
        ref_dir = test_dir.parent / 'ref' / 'mtlx'

        if out_dir is None:
            # Update mode: write directly to reference directory
            cls._out_dir = ref_dir
            cls._ref_differ = None
        else:
            # Compare mode: write to temp dir and compare
            cls._out_dir = Path(out_dir).resolve() / 'mtlx'
            cls._ref_differ = RefDiffer(ref_dir)
        
        os.makedirs(cls._out_dir, exist_ok=True)

    def __init__(self, base_name: str = None, impl_only: bool = False):
        """
        Initialize a GLSL test context.
        
        Args:
            base_name: Optional custom base name for output files.
                       If not provided, uses the test function name.
                       For library-level overrides, use e.g., 'metashade_pbrlib'
            impl_only: If True, skip nodedef generation (for overrides)
        """
        if base_name is None:
            base_name = get_test_func_name()
        super().__init__(base_name, self._out_dir, impl_only=impl_only)

    def __exit__(self, exc_type, exc_value, traceback):
        # Allow parent to generate files first
        success = super().__exit__(exc_type, exc_value, traceback)
        
        if success and self._ref_differ is not None:
            # Verify generated files against references
            if self._nodedef_doc_path is not None:
                self._ref_differ(self._nodedef_doc_path)
            self._ref_differ(self._impl_doc_path)
            self._ref_differ(self._src_path)
            
        return success
