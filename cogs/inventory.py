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
from discord import app_commands
from discord.ext import commands, menus
from core.models import InventoryItem
from core import checks, views, cosmetics

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class InventoryViewSource(menus.ListPageSource):
    bot: CobbleBot

    async def format_page(self, menu: views.Paginator, page: List[InventoryItem]) -> discord.Embed:
        embed = discord.Embed(
            title=":school_satchel: Inventory",
            description="Use the buttons to navigate.\n\n",
            color=discord.Color.dark_embed(),
        )
        embed.set_author(name=menu.interaction.user.display_name, icon_url=menu.interaction.user.display_avatar.url)
        assert embed.description is not None

        embed.description += "\n".join((
            f"{menu.first_page.emoji} Move to first page",
            f"{menu.prev_page.emoji} Move to previous page",
            f"{menu.stop_page.emoji} Stop the pagination",
            f"{menu.next_page.emoji} Move to next page",
            f"{menu.last_page.emoji} Move to last page",
        ))

        embed.description += "\n"
        embed.description += "\u2800" * 36

        for inv_item in page:
            item = menu.bot.items[inv_item.item_id]
            stats = f"Quantity: `{inv_item.quantity}`\n"

            if item.durability is not None:
                stats += f"Durability: {inv_item.durability}/{item.durability}"

            embed.add_field(name=f"{item.emoji} {item.display_name}", value=stats, inline=True)

        return embed


class Inventory(commands.GroupCog):
    """View and manage items in your inventory."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command()
    @checks.has_survival_profile()
    async def view(self, interaction: discord.Interaction):
        """View your inventory."""
        items = await InventoryItem.filter(player=interaction.extras["survival_profile"])

        if len(items) == 0:
            return await interaction.response.send_message(f"{cosmetics.EMOJI_WARNING} Nothing to show yet. The inventory is empty.")

        source = InventoryViewSource(items, per_page=6)
        paginator = views.Paginator(timeout=60.0, bot=self.bot, user=interaction.user, source=source)
        await paginator.start_pagination(interaction)


    @app_commands.command()
    async def info(self, interaction: discord.Interaction, item: str):
        """Shows general information about a specific item.

        Parameters
        ----------
        item:
            The name of item.
        """
        item = item.lower().replace(" ", "_")

        if item not in self.bot.items:
            raise checks.GenericError("Unknown item name provided.")

        data = self.bot.items[item]
        embed = discord.Embed(
            title=f"{data.emoji} {data.display_name}",
            description=data.description,
            color=discord.Color.dark_embed(),
        )

        if data.durability:
            embed.add_field(name="Max Durability", value=data.durability, inline=False)
        else:
            embed.add_field(name="Rarity", value=data.rarity.title())
            embed.add_field(name="Type", value=data.type.title())

        other_info = ""

        if data.crafting_recipe is None and data.smelting_recipe is None:
            other_info += "- Non-craftable"

        if data.crafting_recipe is not None:
            embed.add_field(
                name="Crafting Recipe",
                value=f"\n".join(
                    f"{amount}x {self.bot.items[reqitem].emoji} {self.bot.items[reqitem].display_name}"
                    for reqitem, amount in data.crafting_recipe.items()
                ),
                inline=False,
            )

        if data.smelting_recipe is not None:
            reqitem = self.bot.items[data.smelting_recipe]
            embed.add_field(
                name="Smelting Recipe",
                value=f"{reqitem.emoji} {reqitem.display_name}",
                inline=False,
            )

        if other_info:
            embed.add_field(name="Other Information", value=other_info, inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @checks.has_survival_profile()
    async def discard(self, interaction: discord.Interaction, item: str, quantity: str = "all"):
        """Discards an item from your inventory.

        Parameters
        ----------
        item:
            The name of item.
        quantity:
            The amount to discard. Defaults to "all".
        """
        await interaction.response.defer()

        item = item.lower().replace(" ", "_")

        if item not in self.bot.items:
            raise checks.GenericError("Unknown item name provided.")

        if quantity != "all" and not quantity.isdigit():
            raise checks.GenericError("Quantity must be a valid number. If you want to discard the full amount, pass `all`.")

        data = await InventoryItem.filter(player=interaction.extras["survival_profile"], item_id=item).first()

        if data is None:
            raise checks.GenericError("You don't have this item!")

        item_data = self.bot.items[data.item_id]

        if quantity.lower() == "all":
            amount = data.quantity
        else:
            amount = int(quantity)

        if amount > data.quantity:
            raise checks.GenericError(f"You don't have this much quantity. You only have `{data.quantity}` **{item_data.emoji} {item_data.display_name}**.")

        confirmation = views.Confirmation(user=interaction.user, timeout=30)
        embed = discord.Embed(
            title=f"{cosmetics.EMOJI_DANGER} Are you sure?",
            description=f"You are about to discard `{amount}` **{item_data.emoji} {item_data.display_name}**. After discarding, the item will be lost.",
            color=discord.Color.dark_embed(),
        )

        msg = await interaction.followup.send(view=confirmation, embed=embed, wait=True)

        if await confirmation.wait():
            raise checks.GenericError("Action timed out. No changes made.")

        if confirmation.confirmed:
            await data.remove(amount)
            message = f"Discarded `{amount}` **{item_data.emoji} {item_data.display_name}**"
        else:
            message = f"Action canceled. No changes were made."

        await msg.edit(content=message, embed=None, view=None)

    @info.autocomplete("item")
    @discard.autocomplete("item")
    async def autocomplete_item_name(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=f"{item.display_name}", value=item_id)
            for item_id, item in self.bot.items.items() if current.lower() in item.display_name.lower()
        ]

async def setup(bot: CobbleBot):
    await bot.add_cog(Inventory(bot))
