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

from pathlib import Path
import pytest

# Skip all tests in this directory if MaterialX is not installed
mx = pytest.importorskip("MaterialX")
from metashade.mtlx.util import testing

# Set up test context with this directory
test_dir = Path(__file__).parent
testing.GlslTestContext.setup_class(test_dir)


@pytest.fixture
def stdlib_doc() -> mx.Document:
    """Load the MaterialX standard library."""
    doc = mx.createDocument()
    search_path = mx.getDefaultDataSearchPath()
    mx.loadLibraries(mx.getDefaultDataLibraryFolders(), search_path, doc)
    return doc
