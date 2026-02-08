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

import textwrap
from metashade.targets.hlsl.sm6 import ps_6_0
import io

def test_docstring():
    '''Tests if Python docstrings are translated to comments.'''
    def ps_main(sh) -> 'None':
        '''This is a docstring.
        It has multiple lines.
        '''
        pass

    out = io.StringIO()
    sh = ps_6_0.Generator(out)
    sh.instantiate(ps_main)

    expected_substring = textwrap.dedent(
        '''
        // This is a docstring.
        // It has multiple lines.
        //
        void ps_main()
        '''
    ).strip()

    assert expected_substring in out.getvalue()
