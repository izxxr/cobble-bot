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
from discord.ext import commands
from core.models import Player
from core import checks, views

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class GlobalLeaderboardSource(views.LazyPaginationSource):
    TOP_THREE_EMOJIS = ["\U0001f947", "\U0001f948", "\U0001f949"]

    def __init__(self, per_page: int) -> None:
        self.per_page = per_page

        super().__init__()

    async def get_page(self, page_number: int) -> List[Player]:
        if self.last_page is not None and page_number > self.last_page:
            return await self.get_page(self.last_page)

        offset = page_number * self.per_page
        players = await Player.filter().limit(self.per_page).offset(offset).order_by("-xp")

        if not players:
            # No more players, end reached
            self.last_page = page_number - 1
            return await self.get_page(self.last_page)

        return players

    def exhausted(self) -> bool:
        return self.last_page is not None

    def is_paginating(self) -> bool:
        return True

    async def format_page(self, menu: views.Paginator, page: List[Player]):
        # page contains list of players on current page which are sorted
        # in descending order w.r.t to level and XP.
        embed = discord.Embed(title=":military_medal: Leaderboard • Global", description="", color=discord.Color.dark_embed())
        assert embed.description is not None

        for idx, player in enumerate(page):
            flags = player.get_flags()
            if flags.hide_on_leaderboard:
                name = '_Hidden User_'
            else:
                user = menu.bot.get_user(player.id)
                # FIXME: fetch user if not found?
                if not user:
                    name = '_Unknown User_'
                elif user.discriminator != "0":
                    name = user.display_name + "#" + user.discriminator
                else:
                    name = user.display_name

            if menu.current_page == 0:
                prefix = self.TOP_THREE_EMOJIS[idx] if idx <= 2 else f"{idx + 1}. "
            else:
                prefix = f"{idx + 1}. "

            embed.description += f"{prefix} {name} ({player.xp} XP)\n"

        embed.set_footer(text=f"Page {menu.current_page + 1}")
        return embed


class Leaderboard(commands.GroupCog):
    """View global or guild survival leaderboards."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command(name="global")
    @checks.has_survival_profile()
    async def _global(self, interaction: discord.Interaction) -> None:
        """Shows the global survival leaderboard."""
        source = GlobalLeaderboardSource(per_page=10)
        paginator = views.LazyPaginator(
            timeout=30.0,
            bot=self.bot,
            user=interaction.user,
            source=source,
        )
        await paginator.start_pagination(interaction)


async def setup(bot: CobbleBot):
    await bot.add_cog(Leaderboard(bot))
