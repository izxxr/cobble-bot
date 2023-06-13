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
from tortoise import Tortoise
from discord.ext import commands
from core import cosmetics

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    """Administrative commands for managing bot's behaviour. (Developer only)"""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context[CobbleBot]) -> bool:  # type: ignore
        # Type ignore because Pyright doesn't like cog_check typehints for some reason
        return True if ctx.author.id in self.bot.config.admin_ids else False

    @commands.command()
    async def synctree(self, ctx: commands.Context[CobbleBot], guild_id: Optional[int] = None) -> None:
        """Syncs the application command tree.

        This command can take an optional guild parameter for the guild ID whose commands should
        be synced. If not provided, syncs all global commands. If debug mode is enabled and debug
        guild ID is provided, this command will sync commands for that guild unless another guild
        ID is provided.

        For convenience, if guild ID of "1" is provided, syncs the commands for the guild in which
        the command was ran in.
        """
        if guild_id is None and self.bot.config.debug_guild_id is not None:
            guild_id = self.bot.config.debug_guild_id if self.bot.config.debug_mode else None
            guild = discord.Object(guild_id) if guild_id else None
        elif guild_id == 1:
            guild = ctx.guild
        else:
            guild = None

        commands = await self.bot.tree.sync(guild=guild)
        report = f"Scope: {'Global' if guild is None else 'Guild'}\n" \
                 f"Guild ID: {guild_id}\n" \
                 f"Commands Synced: {len(commands)}"

        await ctx.send(f"{cosmetics.EMOJI_SUCCESS} Synced the command tree successfully. ```{report}```")

    @commands.command()
    async def reload(self, ctx: commands.Context[CobbleBot], extension: str) -> None:
        """Reloads the provided extension.

        The extension name must be provided (including "cogs.") or "*" can be passed
        to reload all extensions.
        """
        if extension == "*":
            to_reload = self.bot.extensions
        else:
            to_reload = [extension]

        total = 0
        for ext in to_reload:
            try:
                await self.bot.reload_extension(ext)
            except Exception as err:
                await ctx.send(f"An error occured while reloading extension `{ext}`: `{err}`")
            else:
                total += 1
        
        await ctx.send(f"{cosmetics.EMOJI_SUCCESS} Reloaded {total} extensions successfully. {len(to_reload) - total} extensions failed to reload.")

    @commands.command()
    async def genschema(self, ctx: commands.Context[CobbleBot]) -> None:
        """Generates Tortoise database schema."""
        await Tortoise.generate_schemas()
        await ctx.send(f"{cosmetics.EMOJI_SUCCESS} Done!")

    @commands.command()
    async def reloadmeta(self, ctx: commands.Context[CobbleBot]) -> None:
        """Reloads the JSON metadata cache."""
        self.bot.cache_data()
        await ctx.send(f"{cosmetics.EMOJI_SUCCESS} Done!")


async def setup(bot: CobbleBot):
    await bot.add_cog(Admin(bot))
