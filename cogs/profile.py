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

from typing import TYPE_CHECKING
from discord import app_commands
from discord.ext import commands
from core.models import Player
from core import cosmetics, checks, views, utils

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class Profile(commands.GroupCog):
    """Manage your survival player profile."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command()
    async def start(self, interaction: discord.Interaction):
        """Start your journey by creating a survival profile."""
        if await Player.exists(id=interaction.user.id):
            return await interaction.response.send_message(f'{cosmetics.EMOJI_ERROR} Your profile already exists.')

        await Player.create(id=interaction.user.id)

        embed = discord.Embed(
            title=":pick: Welcome!",
            description="You have successfully created your survival profile.\n\n" \
                        "Use various commands to collect valuable resources and use them " \
                        "to improve your profile. As you get further, you will level up to " \
                        "higher levels which also gives more amazing perks. Use `/profile view` " \
                        "to view your profile and progress.\n\nGood Luck!",
            color=discord.Color.green(),
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command()
    @checks.has_survival_profile()
    async def delete(self, interaction: discord.Interaction) -> None:
        """Delete your survival profile. This will completely remove any progress you have."""
        embed = discord.Embed(
            title=f"{cosmetics.EMOJI_DANGER} Hol' up!",
            description="You will lose all of your progress upon deleting your survival profile. "\
                        "This action cannot be undone!\n\nPress **Confirm** to proceed or **Cancel** to cancel.",
            color=discord.Color.red(),
        )

        view = views.Confirmation(user=interaction.user)
        view.confirm_button.style = discord.ButtonStyle.danger
        view.cancel_button.style = discord.ButtonStyle.gray

        await interaction.response.send_message(embed=embed, view=view)

        if await view.wait():
            message = f"{cosmetics.EMOJI_WARNING} Timed out. No changes were made."
        else:
            if view.confirmed:
                profile = interaction.extras["survival_profile"]
                await profile.delete()
                message = f"{cosmetics.EMOJI_WARNING} Survival profile deleted successfully."
            else:
                message = f"{cosmetics.EMOJI_SUCCESS} Action cancelled. No changes were made."

        await interaction.edit_original_response(content=message, embed=None, view=None)

    @app_commands.command()
    @checks.has_survival_profile()
    async def view(self, interaction: discord.Interaction) -> None:
        """View your survival profile."""
        await interaction.response.defer()
        profile = interaction.extras["survival_profile"]
        required_xp = profile.get_required_xp()

        embed = discord.Embed(title=f":pick: Survival Profile", color=discord.Color.light_embed())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)

        if profile.level == 0:
            embed.add_field(name="No level yet", value="Use various commands to level up!")
        else:
            embed.add_field(
                name=f"Level {profile.level}",
                value=f"{utils.progress_bar(profile.xp, required_xp)} ({profile.xp}/{required_xp})",
            )

        full_hearts = int(profile.health // 1)
        half_heart = True if (profile.health % 1) == 0.5 else False
        empty_hearts = int(8 - profile.health)

        embed.add_field(
            name="Health",
            value=f"{cosmetics.EMOJI_HEALTH*full_hearts}{cosmetics.EMOJI_HEALTH_HALF if half_heart else ''}{cosmetics.EMOJI_HEALTH_EMPTY*empty_hearts}",
            inline=False,
        )

        total = 0
        discovered = 0

        for biome in self.bot.biomes.values():
            if biome.discovered(profile):
                discovered += 1
            total += 1

        embed.add_field(name="Discovered Biomes", value=f"{discovered}/{total}")
        embed.set_footer(text=f"Survival profile created on {profile.created_at.strftime('%b %d, %Y')}")

        await interaction.followup.send(embed=embed)


async def setup(bot: CobbleBot):
    await bot.add_cog(Profile(bot))
