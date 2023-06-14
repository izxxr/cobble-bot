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

from discord.flags import BaseFlags, flag_value, fill_with_flags

__all__ = (
    'Achievements',
    'PlayerFlags',
)


@fill_with_flags()
class Achievements(BaseFlags):
    """Represents the achievements a user has."""

    @flag_value
    def discovered_biome_desert(self) -> int:
        """Discover the desert biome."""
        return 1 << 0

    @flag_value
    def discovered_biome_ocean(self) -> int:
        """Discover the ocean biome."""
        return 1 << 1


@fill_with_flags()
class PlayerFlags(BaseFlags):
    """Represents the flags a user has."""

    @flag_value
    def died_once(self) -> int:
        """The player has died at least once."""
        return 1 << 0
