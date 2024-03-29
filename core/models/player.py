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

from typing import TYPE_CHECKING, Optional
from core.datamodels import Achievements, PlayerFlags
from tortoise.models import Model
from tortoise import fields
from discord import Embed, Color
from core import cosmetics, utils, constants

if TYPE_CHECKING:
    from discord import Interaction


__all__ = (
    "Player",
    "GuildPlayer",
)


class Player(Model):
    """Represents a survival player."""

    id = fields.IntField(pk=True)
    """The Discord user ID."""

    xp = fields.IntField(default=0)
    """The experience points that the player has."""

    health = fields.FloatField(default=constants.MAX_HEALTH)
    """The player's current health."""

    created_at = fields.DatetimeField(auto_now_add=True)
    """The time when the player profile was created."""

    achievements = fields.BigIntField(default=0)
    """The  achievements of user."""

    flags = fields.BigIntField(default=0)
    """Internal player flags."""

    @property
    def level(self) -> int:
        return self.xp // constants.XP_FACTOR

    @property
    def level_xp(self) -> int:
        return self.xp % constants.XP_FACTOR

    def get_required_xp(self) -> int:
        """Returns the required XP to level up."""
        if self.level == 0:
            return constants.XP_FACTOR

        return self.level * constants.XP_FACTOR

    def get_achievements(self) -> Achievements:
        """Returns the achievements a user has."""
        ach = Achievements()
        ach.value = self.achievements
        return ach

    def get_flags(self) -> PlayerFlags:
        """Returns the flags a user has."""
        flags = PlayerFlags()
        flags.value = self.flags
        return flags

    async def add_xp(self, xp: int, interaction: Optional[Interaction] = None) -> bool:
        """Adds experience points to user.

        Returns True if the user leveled up after addition of XP.
        """
        level_up = False
        old_level = self.level

        self.xp += xp
        await self.save()

        if old_level < self.level:
            level_up = True

        if interaction is not None and level_up:
            embed = Embed(
                title=":arrow_double_up: Level up",
                description=f"You have advanced to level {self.level}!",
                color=Color.dark_embed(),
            )
            await interaction.followup.send(embed=embed, content=f"{interaction.user.mention}")

        return level_up

    async def add_hp(self, hp: float) -> None:
        """Adds HP to player"""
        self.health += hp

        # Ensure we don't exceed max health
        if self.health > constants.MAX_HEALTH:
            self.health = constants.MAX_HEALTH

        await self.save()


    async def remove_hp(
            self,
            hp: float,
            interaction: Optional[Interaction] = None,
            death_message: Optional[str] = None,
        ) -> bool:
        """Removes HP from the player. Returns True if the health dropped to zero (player died)."""
        died = False
        if (self.health - hp) <= 0:
            self.health = constants.MAX_HEALTH
            died = True
        else:
            self.health -= hp


        if interaction and died:
            embed = Embed(
                title=f"{cosmetics.EMOJI_HEALTH_HALF} You died!",
                description=death_message or "You ran out of health.",
                color=Color.red(),  
            )

            flags = self.get_flags()

            if not flags.died_once:
                embed.add_field(
                    name="Tip",
                    value=f"As you progress through your survival journey, various actions such as " \
                          f"exploring or mining etc. will decrease your health. Once it drops to zero, you die. " \
                          "To avoid this, **always eat food to restore your health points.** You can use `/profile view` " \
                          "command to view your health.",
                    inline=False,
                )

                flags.died_once = True
                self.flags = flags.value

            embed.add_field(
                name="Statistics",
                value=f"**Level {self.level} ({self.xp} points)**\n{utils.progress_bar(self.level_xp, self.get_required_xp())} " \
                      f"({self.level_xp}/{self.get_required_xp()})"
            )

            embed.set_footer(text="The level and XP statistics reset upon dying.")
            await interaction.followup.send(embed=embed, content=interaction.user.mention)

        if died:
            self.xp = 0


        await self.save()
        return died


class GuildPlayer(Model):
    """Represents a player related to a guild"""
    player: fields.ForeignKeyRelation[Player] = fields.ForeignKeyField("models.Player", "guild_players")
    guild_id = fields.IntField()
    flags = fields.IntField(default=0)
