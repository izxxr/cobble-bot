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

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class Misc(commands.Cog):
    """Other commands related to bot's information and data."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command()
    async def ping(self, interaction: discord.Interaction) -> None:
        """Shows the current websocket latency of the bot."""
        await interaction.response.send_message(f":ping_pong: Pong! In {round(self.bot.latency * 1000)}ms")

    @app_commands.command()
    async def info(self, interaction: discord.Interaction) -> None:
        """Shows information about Cobble bot."""
        embed = discord.Embed(
            title="Cobble Bot",
            description="Minecraft inspired bot bringing realistic survival experience to Discord servers.",
            color=discord.Color.dark_embed(),
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)  # type: ignore
        embed.add_field(name="Source", value="Cobble is an open source project. Check the [code repository](https://github.com/izxxr/cobble-bot)")
        embed.set_footer(text="Created with ♥ by @izxxr")
        await interaction.response.send_message(embed=embed)

async def setup(bot: CobbleBot):
    await bot.add_cog(Misc(bot))
