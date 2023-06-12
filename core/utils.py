# MIT License

# Copyright (c) 2023 I. Ahmad

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import Any, Callable, Optional
from discord.utils import MISSING

import dotenv
import os

__all__ = (
    "get_config",
)

dotenv.load_dotenv()

def get_config(
    key: str,
    default: Any = MISSING,
    factory: Optional[Callable[[Any], Any]] = None,
    cast_bool: bool = False,
) -> Any:
    """A wrapper function that retrives value for a specific configuration from environment variables.

    The factory argument takes a callable object that takes a single parameter, the value to process.

    If `cast_bool` is set to True, the value is casted to `bool` type. In this case, the raw value
    must either be `true` or `false` (case sensitive) otherwise a ValueError is raised.

    Raises :exc:`KeyError` if key is not found in the environment variables.
    """
    try:
        val = os.environ[key]
    except KeyError:
        if default is not MISSING:
            return default
        raise
    else:
        if factory:
            return factory(val)
        if cast_bool:
            if val == 'true':
                return True
            if val == 'false':
                return False
            raise ValueError(f'the value for variable "{key}" must be either true or false.')
        return val
