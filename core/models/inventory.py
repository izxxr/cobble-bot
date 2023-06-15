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

from typing import TYPE_CHECKING, Optional, Union, List
from tortoise.models import Model
from tortoise import fields

if TYPE_CHECKING:
    from core.models.player import Player


__all__ = (
    "InventoryItem",
)


class InventoryItem(Model):
    """Represents an inventory item."""

    player: fields.ForeignKeyRelation[Player] = fields.ForeignKeyField(model_name="models.Player", related_name="inventories")
    """The Discord user ID."""

    item_id = fields.TextField()
    """The stored item."""

    quantity = fields.IntField(default=1)
    """The quantity of item."""

    durability = fields.IntField(null=True)
    """The durability of item."""

    async def edit_durability(self, durability: int) -> bool:
        """Edits the durability. The passed durability must be a signed integer.

        If upon editing durabilitiy, item is removed from inventory (i.e broken),
        True is returned otherwise False.
        """
        if (self.durability + durability) <= 0:
            await self.delete()
            return True
        else:
            self.durability += durability
            await self.save()

        return False

    async def remove(self, quantity: int = 1) -> bool:         
        """Removes the given quantitiy of inventory item.

        If upon removal of given quantity, item is removed from inventory
        (i.e no more left), True is returned otherwise False.
        """
        if (self.quantity - quantity) <= 0:
            await self.delete()
            return True

        self.quantity -= quantity
        await self.save()

        return False

    @classmethod
    async def add(
        cls,
        player: Player,
        item_id: str,
        quantity: int = 1,
        durability: Optional[int] = None,
    ) -> Union[InventoryItem, List[InventoryItem]]:
        if durability is not None:
            items: List[InventoryItem] = []
            # Anything with durability cannot be stacked
            for _ in range(quantity):
                item = await InventoryItem.create(
                    player=player,
                    item_id=item_id,
                    quantity=1,
                    durability=durability,
                )
                items.append(item)
            return items
        else:
            item = await InventoryItem.filter(player=player, item_id=item_id).first()
            if item is None:
                return await InventoryItem.create(
                    player=player,
                    item_id=item_id,
                    quantity=quantity,
                    durability=durability,
                )
            else:
                item.quantity += quantity
                await item.save()
            
            return item
