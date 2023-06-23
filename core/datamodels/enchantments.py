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

from typing import TYPE_CHECKING, List
from dataclasses import dataclass
from discord.flags import BaseFlags, flag_value, fill_with_flags

if TYPE_CHECKING:
    from core.datamodels import Item

__all__ = (
    'Enchantments',
    'EnchantmentMetadata'
)


ROMAN_NUMBERS = ['I', 'II', 'III', 'IV', 'V']


@dataclass
class EnchantmentMetadata:
    """Represents an enchantment."""
    id: str
    display_name: str
    value: int
    rarity: str
    description: str


@fill_with_flags()
class Enchantments(BaseFlags):
    """Represents the enchantments an enchanted item has."""

    @flag_value
    def unbreaking_1(self) -> int:
        return 1 << 0

    @flag_value
    def unbreaking_2(self) -> int:
        return 1 << 1

    @flag_value
    def unbreaking_3(self) -> int:
        return 1 << 2

    def supported(self, item: Item) -> bool:
        """Indicates whether enhantments enabled in "self" are supported on the "item"."""
        return self.value & item.supported_enchantments == self.value

    def get_names(self) -> List[str]:
        """Get proper display names for the enabled enchantments."""
        names: List[str] = []
        for name, val in self.VALID_FLAGS.items():
            if not self._has_flag(val):
                continue
            
            parts = name.split("_")
            proper = " ".join(parts).title()
            level = int(parts[-1])

            try:
                names.append(proper.replace(parts[-1], ROMAN_NUMBERS[level-1]))
            except IndexError:
                # This should never happen but just to be on the safer side.
                # Roman number probably not available for level.
                names.append(proper)

        return names
