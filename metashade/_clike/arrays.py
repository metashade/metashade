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

class ArrayBase:
    _sh = None
    _element_type = None
    _dims = None

    def __init__():
        pass

    def __getitem__(self, index):
        raise NotImplementedError("Subclasses must implement __getitem__")

    def __setitem__(self, index, value):
        raise NotImplementedError("Subclasses must implement __setitem__")

def create_array(element_type, dims):
    class_name = f"Array_{element_type.__name__}_{dims}"
    array_class = type(
        class_name,
        (ArrayBase,),
        {
            "_element_type": element_type,
            "_dims": dims
        }
    )
    return array_class