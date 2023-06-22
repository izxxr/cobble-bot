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
from core.models import Player, GuildPlayer
from core import checks, views

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot


class LeaderboardSource(views.LazyPaginationSource):
    TOP_THREE_EMOJIS = ["\U0001f947", "\U0001f948", "\U0001f949"]

    def __init__(self, per_page: int) -> None:
        self.per_page = per_page

        super().__init__()

    async def resolve_player_name(self, menu: views.LazyPaginator, player: Player) -> str:
        user = menu.bot.get_user(player.id)
        if user is None:
            try:
                user = menu.bot.fetch_user(player.id)
            except discord.HTTPException:
                return '_Unknown User_'

        return str(user)

    def get_offset(self, page_number: int) -> int:
        return page_number * self.per_page


class GlobalLeaderboardSource(LeaderboardSource):
    def __init__(self, per_page: int) -> None:
        super().__init__(per_page=per_page)

    async def get_page(self, page_number: int) -> List[Player]:
        offset = self.get_offset(page_number)
        players = await Player.filter().limit(self.per_page).offset(offset).order_by("-xp")

        if not players:
            # No more players, end reached
            self.set_last_page(page_number - 1)
            assert self.last_page is not None

            return await self.get_page(self.last_page)

        return players

    async def format_page(self, menu: views.LazyPaginator, page: List[Player]):
        # page contains list of players on current page which are sorted
        # in descending order w.r.t to XP.
        embed = discord.Embed(title=":military_medal: Leaderboard • Global", description="", color=discord.Color.dark_embed())
        assert embed.description is not None
        
        offset = self.get_offset(menu.current_page)

        for idx, player in enumerate(page):
            flags = player.get_flags()
            if flags.hide_on_leaderboard:
                name = '_Hidden User_'
            else:
                name = await self.resolve_player_name(menu, player)

            rank = offset + idx + 1
            prefix = self.TOP_THREE_EMOJIS[rank - 1] if rank <= 3 else f"{rank}. "

            embed.description += f"{prefix} {name} ({player.xp} XP)\n"

        embed.set_footer(text=f"Page {menu.current_page + 1}")
        return embed


class GuildLeaderboardSource(LeaderboardSource):
    TOP_THREE_EMOJIS = ["\U0001f947", "\U0001f948", "\U0001f949"]

    def __init__(self, per_page: int, guild: discord.Guild) -> None:
        self.guild = guild
        self._players: List[Player] = []  # cached players (rank higher -> lower)

        super().__init__(per_page=per_page)

    async def get_page(self, page_number: int) -> List[GuildPlayer]:
        offset = page_number * self.per_page
        # I don't think this is possible without raw SQL.
        sql = f"""SELECT player_id FROM guildplayer INNER JOIN player ON 
                 guildplayer.player_id = player.id ORDER BY player.xp DESC
                 LIMIT {self.per_page} OFFSET {offset};"""

        players = await GuildPlayer.raw(sql)
        if not players:
            # No more players, end reached
            self.set_last_page(page_number - 1)
            assert self.last_page is not None

            return await self.get_page(self.last_page)

        return players  # type: ignore

    def exhausted(self) -> bool:
        return self.last_page is not None

    def is_paginating(self) -> bool:
        return True

    async def format_page(self, menu: views.LazyPaginator, page: List[GuildPlayer]):
        embed = discord.Embed(title=":military_medal: Leaderboard • Guild", description="", color=discord.Color.dark_embed())
        assert embed.description is not None

        offset = self.get_offset(menu.current_page)

        for idx, guild_player in enumerate(page):
            await guild_player.fetch_related("player")
            name = await self.resolve_player_name(menu, guild_player.player)

            rank = offset + idx + 1
            prefix = self.TOP_THREE_EMOJIS[rank - 1] if rank <= 3 else f"{rank}. "

            embed.description += f"{prefix} {name} ({guild_player.player.xp} XP)\n"

        embed.set_footer(text=f"Page {menu.current_page + 1} • Only users who have used the bot command at least once in the server are shown.")
        return embed


class Leaderboard(commands.GroupCog):
    """View global or guild survival leaderboards."""
    def __init__(self, bot: CobbleBot) -> None:
        self.bot = bot

    @app_commands.command(name="global")
    @checks.has_survival_profile()
    async def _global(self, interaction: discord.Interaction) -> None:
        """Shows the global survival leaderboard."""
        await interaction.response.defer()

        source = GlobalLeaderboardSource(per_page=10)
        paginator = views.LazyPaginator(
            timeout=30.0,
            bot=self.bot,
            user=interaction.user,
            source=source,
        )
        await paginator.start_pagination(interaction)

    @app_commands.command()
    @app_commands.guild_only()
    @checks.has_survival_profile()
    async def guild(self, interaction: discord.Interaction) -> None:
        """Shows the guild survival leaderboard."""
        assert interaction.guild is not None
        await interaction.response.defer()

        source = GuildLeaderboardSource(per_page=10, guild=interaction.guild)
        paginator = views.LazyPaginator(
            timeout=30.0,
            bot=self.bot,
            user=interaction.user,
            source=source,
        )
        await paginator.start_pagination(interaction)


async def setup(bot: CobbleBot):
    await bot.add_cog(Leaderboard(bot))
