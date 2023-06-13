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

from typing import Tuple, Any, Optional, Dict
from dataclasses import dataclass

__all__ = (
    'LootTable',
    'LootTableItem',
)


@dataclass
class LootTable:
    """Represents a loot table.
    
    Loot table determines the loot that can be obtained from a specific action. It
    also includes the probability and various conditions that must be satisfied to
    obtain a specific loot.
    """
    name: str
    items: Dict[str, LootTableItem]


@dataclass
class LootTableItem:
    """Represents an item associated to a loot table."""

    id: str
    probability: float
    quantity: Tuple[int, int]
    durability: Optional[Tuple[int, int]] = None

    def __post_init__(self, *args: Any, **kw: Any) -> None:
        self.durability = tuple(self.durability) if self.durability else None
        self.quantity = tuple(self.quantity)
