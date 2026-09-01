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

import MaterialX as mx

from metashade.util.testing import get_test_func_name, RefDiffer
from metashade.mtlx.generate import GlslGeneratorContext


class TestContextBase:
    """Shared output/ref directory configuration for MaterialX test contexts.

    Call :meth:`setup_class` once per test session (typically from a
    ``conftest.py`` fixture) to configure paths.
    """

    @classmethod
    def setup_class(cls, test_dir: Path):
        cls._parent_dir = test_dir

        # Consistent with metashade.util.testing
        out_dir = os.getenv('METASHADE_PYTEST_OUT_DIR', None)

        ref_dir_env = os.getenv('METASHADE_MTLX_PYTEST_REF_DIR', None)
        if ref_dir_env:
            ref_dir = Path(ref_dir_env).resolve()
        else:
            # Assuming tests are in tests/mtlx, refs are in tests/ref/mtlx
            ref_dir = test_dir.parent / 'ref' / 'mtlx'

        if out_dir is None:
            # Update mode: write directly to reference directory.
            # No comparison — the developer examines diffs in git.
            cls._out_dir_root = ref_dir
            cls._ref_dir_root = None
        else:
            # Compare mode: write to temp dir and compare
            cls._out_dir_root = Path(out_dir).resolve() / 'mtlx'
            cls._ref_dir_root = ref_dir

        os.makedirs(cls._out_dir_root, exist_ok=True)

    @classmethod
    def _resolve_dirs(cls, subdir: str = None):
        """Return ``(out_dir, ref_dir)`` for *subdir*, creating out_dir."""
        out_dir = cls._out_dir_root
        ref_dir = cls._ref_dir_root
        if subdir is not None:
            out_dir = out_dir / subdir
            if ref_dir is not None:
                ref_dir = ref_dir / subdir
        os.makedirs(out_dir, exist_ok=True)
        return out_dir, ref_dir


class GlslTestContext(TestContextBase, GlslGeneratorContext):
    def __init__(self, base_name: str = None, impl_only: bool = False,
                 subdir: str = None):
        """
        Initialize a GLSL test context.

        Args:
            base_name: Optional custom base name for output files.
                       If not provided, uses the test function name.
                       For library-level overrides, use e.g., 'metashade_pbrlib'
            impl_only: If True, skip nodedef generation (for overrides)
            subdir: Optional subdirectory within the output/ref dirs.
                    Used to scope generated files per experiment/environment.
        """
        if base_name is None:
            base_name = get_test_func_name()

        out_dir, self._ref_dir = self._resolve_dirs(subdir)
        super().__init__(base_name, out_dir, impl_only=impl_only)

    def __exit__(self, exc_type, exc_value, traceback):
        success = super().__exit__(exc_type, exc_value, traceback)

        if success and self._ref_dir is not None:
            ref_differ = RefDiffer(self._ref_dir)

            if self._nodedef_doc_path is not None:
                ref_differ(self._nodedef_doc_path)
            ref_differ(self._impl_doc_path)
            ref_differ(self._src_path)

        return success


class MtlxTestContext(TestContextBase):
    """Context manager for writing and RefDiffer'ing a pure .mtlx document.

    Target-agnostic: use for artifacts like the surfaceshader nodegraph
    that are independent of any specific codegen target (GLSL, Slang, etc.).
    """

    def __init__(self, file_name: str, subdir: str = None):
        out_dir, self._ref_dir = self._resolve_dirs(subdir)
        self._path = out_dir / file_name
        self._doc = None

    def __enter__(self):
        return self

    def write(self, doc: mx.Document):
        self._doc = doc

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None or self._doc is None:
            return False
        mx.writeToXmlFile(self._doc, str(self._path))
        if self._ref_dir is not None:
            RefDiffer(self._ref_dir)(self._path)
        return True
