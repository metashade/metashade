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

import time

class TimedScope:
    def __init__(self, start_message : str, end_message : str = None):
        self._start_ns = None
        self._start_message = start_message
        self._end_message = end_message

    def __enter__(self):
        print(
            f'{self._start_message}... ',
            end = '' if self._end_message is None else '\n'
        )
        self._start_ns = time.perf_counter_ns()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed_ms = (time.perf_counter_ns() - self._start_ns) / 1e6
        if self._end_message is not None:
            print(f'{self._end_message}: ', end = '')
        print(f'{elapsed_ms:0.3f}ms')
