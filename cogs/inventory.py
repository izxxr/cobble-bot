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

from typing import TYPE_CHECKING, List, Union
from discord import app_commands
from discord.ext import commands, menus
from core.models import InventoryItem, Player
from core.constants import MAX_HEALTH
from core import checks, views, cosmetics, datamodels

import math
import random
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

            embed.add_field(name=f"{item.name(bold=False)}", value=stats, inline=True)

        return embed


class Inventory(commands.GroupCog):
    """View and manage items in your inventory."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot
        self._inject_command_extras()

    def _inject_command_extras(self) -> None:
        for command in self.walk_app_commands():
            command.extras["guild_user"] = True

    def _is_usable(self, item: datamodels.Item) -> bool:
        return any((
            item.food_hp_restored is not None,
        ))

    async def _use_item(self, inventory_item: InventoryItem, quantity: int, player: Player) -> Union[bool, discord.Embed, str]:
        data = self.bot.items[inventory_item.item_id]

        if data.food_hp_restored is not None:
            # food item
            hp_gained = data.food_hp_restored * quantity
            if hp_gained > MAX_HEALTH:
                hp_gained = MAX_HEALTH

            await player.add_hp(hp_gained)
            return f"{cosmetics.EMOJI_HEALTH_HALF} Ate {quantity} {data.name()} to restore `{hp_gained}` HP."
        else:
            return False

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
            title=data.name(bold=False),
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
                    f"{amount}x {self.bot.items[reqitem].name(bold=False)}"
                    for reqitem, amount in data.crafting_recipe.items()
                ),
                inline=False,
            )
            embed.add_field(
                name="Crafted Quantity",
                value=str(data.crafting_quantity),
            )

        if data.smelting_recipe is not None:
            reqitem = self.bot.items[data.smelting_recipe]
            embed.add_field(
                name="Smelting Recipe",
                value=reqitem.name(bold=False),
                inline=False,
            )

        if data.smelting_product is not None:
            reqitem = self.bot.items[data.smelting_product]
            embed.add_field(
                name="Smelting Product",
                value=reqitem.name(bold=False),
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
            raise checks.GenericError(f"You don't have this much quantity. You only have `{data.quantity}` {item_data.name()}.")

        confirmation = views.Confirmation(user=interaction.user, timeout=30)
        embed = discord.Embed(
            title=f"{cosmetics.EMOJI_DANGER} Are you sure?",
            description=f"You are about to discard `{amount}` {item_data.name()}. After discarding, the item will be lost.",
            color=discord.Color.dark_embed(),
        )

        msg = await interaction.followup.send(view=confirmation, embed=embed, wait=True)

        if await confirmation.wait():
            raise checks.GenericError("Action timed out. No changes made.")

        if confirmation.confirmed:
            await data.remove(amount)
            message = f"Discarded `{amount}` {item_data.name()}"
        else:
            message = f"Action canceled. No changes were made."

        await msg.edit(content=message, embed=None, view=None)

    @app_commands.command()
    @checks.has_survival_profile()
    async def craft(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        """Craft an item.

        Parameters
        ----------
        item:
            The name of item.
        quantity:
            The amount to craft. Defaults to 1.
        """
        embed = discord.Embed(title="<a:minecraft_crafting_table_working:1118527217400549466> Crafting...")
        await interaction.response.send_message(embed=embed)

        item = item.lower().replace(" ", "_")

        if item not in self.bot.items:
            raise checks.GenericError("Unknown item name provided.")

        item_data = self.bot.items[item]
        profile = interaction.extras["survival_profile"]

        if item_data.crafting_recipe is None:
            raise checks.GenericError("This item is not craftable.")

        for item_id, crafting_quantity in item_data.crafting_recipe.items():
            required_item_data = self.bot.items[item_id]
            required_item = await InventoryItem.filter(
                player=profile,
                item_id=item_id,
            ).first()

            error_message = ""
            if required_item is None:
                error_message = f"{cosmetics.EMOJI_WARNING} You need `{crafting_quantity}` {required_item_data.name()}. You have none."
            else:
                required_quantity = crafting_quantity * quantity
                if required_quantity > required_item.quantity:
                    error_message = f"{cosmetics.EMOJI_WARNING} You need `{required_quantity}` {required_item_data.name()}. You currently have `{required_item.quantity}` of it."
                else:
                    await required_item.remove(required_quantity)

            if error_message:
                return await interaction.edit_original_response(content=error_message, embed=None)

        # At this point, all conditions have been passed and player should be eligible to
        # craft the given item so add it to inventory.
        quantity_crafted = quantity * item_data.crafting_quantity
        await InventoryItem.add(player=profile, item_id=item, quantity=quantity_crafted, durability=item_data.durability)
        await interaction.edit_original_response(content=f":carpentry_saw: Crafted `{quantity_crafted}` {item_data.name()}", embed=None)

    @app_commands.command()
    @checks.has_survival_profile()
    async def smelt(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        """Smelts an item.

        Parameters
        ----------
        item:
            The name of item to smelt.
        quantity:
            The amount to smelt. Defaults to 1.
        """
        item = item.lower().replace(" ", "_")

        if item not in self.bot.items:
            raise checks.GenericError("Unknown item name provided.")

        data = self.bot.items[item]
        if data.smelting_product is None:
            raise checks.GenericError("This item cannot be smelted.")

        embed = discord.Embed(title="<a:minecraft_lit_furnace_blink:1119501606988296192> Smelting...")
        await interaction.response.send_message(embed=embed)

        profile: Player = interaction.extras["survival_profile"]
        inv_item = await InventoryItem.filter(player=profile, item_id=item).first()

        if inv_item is None:
            return await interaction.edit_original_response(
                content=f"{cosmetics.EMOJI_WARNING} You don't have this item.",
                embed=None,
            )
        if inv_item.quantity < quantity:
            return await interaction.edit_original_response(
                content=f"{cosmetics.EMOJI_WARNING} You only have `{inv_item.quantity}` {data.name()}.",
                embed=None,
            )

        item_formed = self.bot.items[data.smelting_product]
        coal = await InventoryItem.filter(player=profile, item_id="coal").first()
        coal_data = self.bot.items["coal"]

        if coal is None:
            return await interaction.edit_original_response(
                content=f"{cosmetics.EMOJI_WARNING} You need {data.name()} to smelt items.",
                embed=None,
            )

        required_fuel = math.ceil(quantity / 4)
        if coal.quantity < required_fuel:
            message = f"{cosmetics.EMOJI_WARNING} You need `{required_fuel}` {coal_data.name()} " \
                      f"to smelt `{quantity}` {data.name()}. You only have `{coal.quantity}` of coal."

            return await interaction.edit_original_response(
                content=message,
                embed=None,
            )

        await coal.remove(required_fuel)
        await inv_item.remove(quantity)
        await InventoryItem.add(player=profile, item_id=item_formed.id, quantity=quantity)

        xp_gained = random.randint(1, 5)
        embed = discord.Embed(
            title=":wood: Smelting",
            description=f"Successfully smelted `{quantity}` {data.name()}",
            color=discord.Color.dark_embed(),
        )
        embed.add_field(name="Product", value=f"{quantity}x {item_formed.name()}")
        embed.add_field(name="Fuel Used", value=f"{required_fuel}x {coal_data.name()}")
        embed.set_footer(text=f"+{xp_gained} XP")

        await interaction.edit_original_response(embed=embed)
        await profile.add_xp(xp_gained, interaction)

    @app_commands.command()
    @checks.has_survival_profile()
    async def use(self, interaction: discord.Interaction, item: str, quantity: int = 1):
        """Uses an item (e.g. eat food).

        Parameters
        ----------
        item:
            The name of item to use.
        quantity:
            The quantity to use. Defaults to 1.
        """
        item = item.lower().replace(" ", "_")
        if item not in self.bot.items:
            raise checks.GenericError("Unknown item name provided.")

        await interaction.response.defer()

        profile = interaction.extras["survival_profile"]
        inv_item = await InventoryItem.filter(item_id=item, player=profile).first()

        if inv_item is None:
            raise checks.GenericError("You don't have this item.")

        result = await self._use_item(inv_item, quantity, profile)

        if isinstance(result, str):
            await interaction.followup.send(content=result)
        elif isinstance(result, discord.Embed):
            await interaction.followup.send(embed=result)
        else:
            raise checks.GenericError("This item cannot be used.")

    @use.autocomplete("item")
    async def autocomplete_item_name_usable(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=f"{item.display_name}", value=item_id)
            for item_id, item in self.bot.items.items()
            if current.lower() in item.display_name.lower() and self._is_usable(item)
        ]

    @smelt.autocomplete("item")
    async def autocomplete_item_name_smeltable(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=f"{item.display_name}", value=item_id)
            for item_id, item in self.bot.items.items()
            if current.lower() in item.display_name.lower() and item.smelting_product
        ]

    @craft.autocomplete("item")
    async def autocomplete_item_name_craftable(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=f"{item.display_name}", value=item_id)
            for item_id, item in self.bot.items.items()
            if current.lower() in item.display_name.lower() and item.crafting_recipe
        ]

    @info.autocomplete("item")
    @discard.autocomplete("item")
    async def autocomplete_item_name(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=f"{item.display_name}", value=item_id)
            for item_id, item in self.bot.items.items()
            if current.lower() in item.display_name.lower()
        ]

async def setup(bot: CobbleBot):
    await bot.add_cog(Inventory(bot))
