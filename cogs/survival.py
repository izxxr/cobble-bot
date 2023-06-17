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
from tortoise.expressions import Q
from core.models import Player, InventoryItem
from core import checks, datamodels, views, cosmetics

import discord
import random

if TYPE_CHECKING:
    from core.bot import CobbleBot

    ObtainedLootT = List[Tuple[datamodels.Item, int, Optional[int]]]


# Sorted by priority (lowest -> highest)
# e.g. if a player has both wooden and stone pickaxe in their inventory
# stone pickaxe would be used for mining as it takes higher priority.
# Also note that though gold tools are weak, they still follow the normal
# priority order (so essentially, if one doesn't want gold tools used, discard them).
PICKAXES_IDS = (
    "wooden_pickaxe",
    "stone_pickaxe",
    "iron_pickaxe",
    "gold_pickaxe",
    "diamond_pickaxe",
)


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

    async def _process_loot_table(self, profile: Player, table: datamodels.LootTable) -> ObtainedLootT:
        obtained_loot: ObtainedLootT = []

        for item_id, item in table.items.items():
            if not random.random() < item.probability:
                continue
            
            quantity = random.randint(item.quantity[0], item.quantity[1])
            durability = None

            if item.durability is not None:
                durability = random.randint(item.durability[0], item.durability[1])

            obtained_loot.append((self.bot.items[item_id], quantity, durability))

        for item, quantity, durability in obtained_loot:
            await InventoryItem.add(
                player=profile,
                item_id=item.id,
                quantity=quantity,
                durability=durability,
            )

        return obtained_loot

    def _generate_loot_embed(self, loot: ObtainedLootT, title: str, description: str, xp_gained: Optional[int] = None) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.dark_embed(),
        )

        embed.add_field(name="Collected Loot", value="\n".join(
                                                    f"{x[1]}x {x[0].emoji} {x[0].display_name}"
                                                    for x in loot))

        if xp_gained:
            embed.set_footer(text=f"+{xp_gained} XP")

        return embed

    def _item_break_embed(self, item_id: str) -> discord.Embed:
        item = self.bot.items[item_id]
        embed = discord.Embed(
            title=":adhesive_bandage: Item Broken",
            description=f"Your **{item.emoji} {item.display_name}** just broke.",
            color=discord.Color.red(),
        )

        if item.crafting_recipe is not None:
            embed.set_footer(text="This item can be recrafted.")

        return embed

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(checks.cooldown_factory(1, 600))
    @checks.has_survival_profile()
    async def explore(self, interaction: discord.Interaction):
        """Explore different biomes and collect valuables and other resources."""
        profile: Player = interaction.extras["survival_profile"]

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

        hp = random.choice((0, 0.5))
        dead = await profile.remove_hp(hp, interaction, "You died while exploring the secrets that shouldn't be explored.")

        if dead:
            return await interaction.delete_original_response()

        assert view.selected_biome is not None

        loot_table = self.bot.loot_tables["exploration_" + view.selected_biome.id]
        loot = await self._process_loot_table(profile, loot_table)
        xp_gained = len(loot) * random.randint(1, 5)

        embed = self._generate_loot_embed(
            loot,
            title=":hiking_boot: Exploration",
            description=f"You explored the **{view.selected_biome.emoji} {view.selected_biome.display_name}**",
            xp_gained=xp_gained,
        )

        await interaction.edit_original_response(embed=embed)
        await profile.add_xp(xp_gained, interaction)

        discovered_biome = None
        for _, biome in self.bot.biomes.items():
            if biome.discovered(profile) or not random.random() < biome.discovery_probability:
                continue
            else:
                discovered_biome = biome
                break

        if discovered_biome is None:
            return

        achievements = profile.get_achievements()
        achievements.value |= discovered_biome.discovery_achievement

        profile.achievements = achievements.value  # type: ignore
        await profile.save()

        embed = discord.Embed(
            title=":sunrise_over_mountains: New biome discovered",
            description="You just discovered a new biome! Discovering new biomes opens up new loot that can be obtained from exploration.",
            color=discord.Color.dark_embed(),
        )

        embed.add_field(name="Biome", value=f"{discovered_biome.emoji} {discovered_biome.display_name}")
        embed.add_field(name="Information", value=discovered_biome.description)
        embed.add_field(name="Rarity", value=discovered_biome.rarity.title())
        embed.set_image(url=discovered_biome.background)

        await interaction.followup.send(embed=embed, content=f"{interaction.user.mention}")

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(checks.cooldown_factory(1, 300))
    @checks.has_survival_profile()
    async def fish(self, interaction: discord.Interaction) -> None:
        """Obtain resources from fishing."""
        await interaction.response.send_message(
            embed=discord.Embed(title=f"<a:minecraft_fishing:1118781577418252358> Fishing...")
        )

        profile = interaction.extras["survival_profile"]
        invitem = await InventoryItem.filter(player=profile, item_id="fishing_rod").first()

        if invitem is None:
            fishing_rod = self.bot.items["fishing_rod"]
            return await interaction.response.send_message(f"{cosmetics.EMOJI_WARNING} You need a **{fishing_rod.emoji} {fishing_rod.display_name}** to fish.")

        loot_table = self.bot.loot_tables["fishing"]
        obtained_loot = await self._process_loot_table(profile, loot_table)
        xp_gained = random.randint(1, 3) * len(obtained_loot)
        embed = self._generate_loot_embed(
            obtained_loot,
            title=":fishing_pole_and_fish: Fishing",
            description="You went for fishing and obtained the following loot",
            xp_gained=xp_gained,
        )

        await interaction.edit_original_response(embed=embed)
        await profile.add_xp(xp_gained, interaction)

        broken = await invitem.edit_durability(-random.randint(1, 2)*len(obtained_loot))
        if broken:
            await interaction.followup.send(embed=self._item_break_embed("fishing_rod"))

    @app_commands.command()
    @checks.has_survival_profile()
    async def mine(self, interaction: discord.Interaction):
        """Go for mining to collect minerals and other resources."""
        await interaction.response.defer()

        player: Player = interaction.extras["survival_profile"]

        pickaxes = await InventoryItem.filter(Q(item_id__in=PICKAXES_IDS), player=player)
        pickaxes.sort(key=lambda x: PICKAXES_IDS.index(x.item_id))

        if not pickaxes:
            raise checks.GenericError("You must have a pickaxe in order to mine.")

        await interaction.followup.send(
            embed=discord.Embed(title="<a:minecraft_mining:1119496609835786240> Mining...")
        )

        died = await player.remove_hp(random.choice((0.5, 1)), interaction, death_message="You died while mining deep down in the caves.")
        if died:
            return await interaction.delete_original_response()

        pickaxe = pickaxes[-1]  # pickaxes list is sorted by priority (lowest -> highest)

        table = self.bot.loot_tables["mining_" + pickaxe.item_id]
        loot = await self._process_loot_table(player, table)
        xp_gained = random.randint(1, 3) * len(loot)

        embed = self._generate_loot_embed(
            loot=loot,
            title=":pick: Mining",
            description="You went for mining and collected the following loot.",
            xp_gained=xp_gained,
        )

        await interaction.edit_original_response(embed=embed)
        await player.add_xp(xp_gained, interaction)
    
        broken = await pickaxe.edit_durability(-random.randint(1, 2)*len(loot))
        if broken:
            await interaction.followup.send(embed=self._item_break_embed(pickaxe.item_id))

async def setup(bot: CobbleBot):
    await bot.add_cog(Survival(bot))
