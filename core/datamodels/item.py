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

from typing import Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass
from .enchantments import Enchantments

if TYPE_CHECKING:
    from core.models import InventoryItem

__all__ = (
    'Item',
)


@dataclass
class Item:
    """Represents an obtainable item."""

    id: str
    display_name: str
    description: str
    rarity: str
    type: str
    emoji: str
    supported_enchantments: int = 0
    crafting_quantity: int = 1
    crafting_recipe: Optional[Dict[str, int]] = None
    smelting_recipe: Optional[str] = None
    smelting_product: Optional[str] = None
    durability: Optional[int] = None
    food_hp_restored: Optional[float] = None
    enchanted_emoji: Optional[str] = None

    def enchantable(self) -> bool:
        return self.supported_enchantments != 0

    def name(self, inv_item: Optional[InventoryItem] = None, *, bold: bool = True) -> str:
        if inv_item and inv_item.enchantments != 0:
            n = f"{self.enchanted_emoji if self.enchanted_emoji else self.emoji} Enchanted {self.display_name}"
        else:
            n = f"{self.emoji} {self.display_name}"

        return f"**{n}**" if bold else n

    def get_supported_enchantments(self) -> Enchantments:
        ench = Enchantments()
        ench.value = self.supported_enchantments
        return ench
