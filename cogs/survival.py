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

from typing import TYPE_CHECKING, Optional, List, Tuple
from discord.ext import commands
from discord import app_commands, ui
from core.models import Player
from core import checks, datamodels, views, cosmetics

import discord
import asyncio
import random

if TYPE_CHECKING:
    from core.bot import CobbleBot


class ExplorationBiomeSelectView(views.AuthorizedView):
    def __init__(self, user: discord.abc.Snowflake, bot: CobbleBot):
        super().__init__(timeout=180.0, user=user)

        self.selected_biome: Optional[datamodels.Biome] = None
        self.selector = ExplorationBiomeSelect(bot)
        self.add_item(self.selector)


class ExplorationBiomeSelect(ui.Select[ExplorationBiomeSelectView]):
    def __init__(self, bot: CobbleBot) -> None:
        super().__init__(placeholder="Select a biome.")
        self.bot = bot

    async def callback(self, interaction: discord.Interaction[CobbleBot]) -> None:  # type: ignore
        assert self.view is not None

        await interaction.response.defer()
        self.view.stop()
        self.view.selected_biome = self.bot.biomes[self.values[0]]

    def populate(self, player: Player) -> None:
        biomes = self.bot.biomes

        for biome_id, biome in biomes.items():
            if not biome.discovered(player):
                continue

            self.add_option(
                label=biome.display_name,
                value=biome_id,
                description=biome.description,
                emoji=biome.emoji,
            )


class Survival(commands.Cog):
    """Commands for collecting resources and valuables."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command()
    @checks.has_survival_profile()
    async def explore(self, interaction: discord.Interaction):
        """Explore different biomes and collect valuables and other resources."""
        profile = interaction.extras["survival_profile"]

        view = ExplorationBiomeSelectView(interaction.user, self.bot)
        view.selector.populate(profile)

        embed = discord.Embed(
            title=":hiking_boot: Explore • Select Biome",
            description="Select the biome to explore.\n\nAs you keep exploring, " \
                        "you will discover more biomes. Each biome has specific features and loot. " \
                        "Certain biomes are common while others are rare. The rarer a biome is, the more " \
                        "valuable its loot will be.",
            color=discord.Color.dark_embed(),
        )

        await interaction.response.send_message(embed=embed, view=view)
        if await view.wait():
            return await interaction.edit_original_response(
                embed=None,
                view=None,
                content=f"{cosmetics.EMOJI_ERROR} Timed out."
            )

        embed = discord.Embed(
            title="<a:minecraft_steve_walk_side:1118071620360216606> Exploring...",
            color=discord.Color.dark_embed(),
        )

        await interaction.edit_original_response(embed=embed, view=None)

        assert view.selected_biome is not None
        loot_table = self.bot.loot_tables["exploration_" + view.selected_biome.id]

        loot: List[Tuple[datamodels.Item, int, Optional[int]]] = []
        for item_id, item in loot_table.items.items():
            if not random.random() < item.probability:
                continue
            
            quantity = random.randint(item.quantity[0], item.quantity[1])
            durability = random.randint(item.durability[0], item.durability[1]) if item.durability else None

            loot.append((self.bot.items[item_id], quantity, durability))

        await asyncio.sleep(2)

        embed = discord.Embed(
            title=f":hiking_boot: Exploration",
            description=f"You explored the **{view.selected_biome.emoji} {view.selected_biome.display_name}**",
            color=discord.Color.dark_embed(),
        )

        # TODO: Add loot to inventory
        # TODO: Implement biome discoveries
        # TODO: Implement structures discoveries

        embed.add_field(
            name="Collected Loot",
            value="\n".join(
                f"{x[1]}x {x[0].emoji} {x[0].display_name}"
                for x in loot
            )
        )

        await interaction.edit_original_response(embed=embed)


async def setup(bot: CobbleBot):
    await bot.add_cog(Survival(bot))
