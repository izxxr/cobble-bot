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

from core.datamodels import Achievements
from tortoise.models import Model
from tortoise import fields

__all__ = (
    "Player",
)


class Player(Model):
    """Represents a survival player."""

    id = fields.IntField(pk=True)
    """The Discord user ID."""

    level = fields.IntField(default=0)
    """Player's current level."""

    xp = fields.IntField(default=0)
    """The experience points that the player has."""

    health = fields.FloatField(default=8)
    """The player's current health."""

    created_at = fields.DatetimeField(auto_now_add=True)
    """The time when the player profile was created."""

    achievements = fields.BigIntField(default=0)
    """The  achievements of user."""

    def get_required_xp(self) -> int:
        """Returns the required XP to level up."""
        return self.level * 100

    def get_achievements(self) -> Achievements:
        """Returns the achievements a user has."""
        ach = Achievements()
        ach.value = self.achievements
        return ach
