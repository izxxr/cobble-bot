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

from typing import Optional, Any, Dict, TYPE_CHECKING
from typing_extensions import Self
from discord.ext import menus
from discord import ui, ButtonStyle
from core import cosmetics

import discord

if TYPE_CHECKING:
    from core.bot import CobbleBot

__all__ = (
    'AuthorizedView',
    'Confirmation',
    'Paginator',
)


class AuthorizedView(ui.View):
    def __init__(self, *, timeout: Optional[float] = 180, user: discord.abc.Snowflake):
        super().__init__(timeout=timeout)
        self.user = user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f'{cosmetics.EMOJI_ERROR} You cannot interact with this!')
            return False

        return True


class Confirmation(AuthorizedView):
    def __init__(self, *, timeout: Optional[float] = 180, user: discord.abc.Snowflake):
        super().__init__(timeout=timeout, user=user)
        self.confirmed: Optional[bool] = None

    @ui.button(label='Confirm', style=ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.confirmed = True
        self.stop()

    @ui.button(label='Cancel', style=ButtonStyle.gray)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.confirmed = False
        self.stop()

# This class implementation is too hacky and overrides a lot of internals of
# the discord.ext.menus package and that is the reason why the typing is so
# messed up here. Unfortunately, there is no other "good" solution to avoid
# this typing dumpster fire.
class Paginator(AuthorizedView, menus.MenuPages):
    def __init__(
            self,
            *,
            timeout: Optional[float] = 180,
            bot: CobbleBot,
            user: discord.abc.Snowflake,
            source: menus.ListPageSource,
        ):

        super().__init__(timeout=timeout, user=user)

        self.bot = bot
        self._source = source
        self.current_page = 0
        self.ctx = None
        self.interaction: discord.Interaction = discord.utils.MISSING
        self.message: Optional[discord.Message] = None

    async def start_pagination(self, interaction: discord.Interaction) -> None:
        await self._source._prepare_once()  # type: ignore
        self.interaction = interaction
        await self.send_initial_response(interaction)

    async def show_page(self, page_number: int):
        assert self.interaction is not None

        page = await self._source.get_page(page_number)  # type: ignore
        self.current_page = page_number
        self._update_buttons_state()

        kwargs = await self._get_kwargs_from_page(page)  # type: ignore
        await self.interaction.edit_original_response(**kwargs)

    async def send_initial_response(self, interaction: discord.Interaction) -> None:
        page = await self._source.get_page(0)  # type: ignore
        kwargs = await self._get_kwargs_from_page(page)  # type: ignore

        self._update_buttons_state()
        await interaction.response.send_message(**kwargs)

    async def _get_kwargs_from_page(self, page: menus.PageSource) -> Any:
        value: Dict[str, Any] = await super()._get_kwargs_from_page(page)  # type: ignore
        if 'view' not in value:
            value.update({'view': self})
        return value

    def _update_buttons_state(self) -> None:
        last_page_idx = self._source.get_max_pages() - 1

        if self.current_page == 0:
            self.next_page.disabled = False
            self.last_page.disabled = False
            self.first_page.disabled = True
            self.prev_page.disabled = True
        elif self.current_page == last_page_idx:
            self.next_page.disabled = True
            self.last_page.disabled = True
            self.first_page.disabled = False
            self.prev_page.disabled = False
        else:
            self.next_page.disabled = False
            self.last_page.disabled = False
            self.first_page.disabled = False
            self.prev_page.disabled = False

    @ui.button(emoji='\U000023ea', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: ui.Button[Self]):
        await interaction.response.defer()
        await self.show_page(0)

    @ui.button(emoji='\U000025c0', style=discord.ButtonStyle.blurple)
    async def prev_page(self, interaction: discord.Interaction, button: ui.Button[Self]):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page - 1)  # type: ignore

    @ui.button(emoji='\U000023f9', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction: discord.Interaction, button: ui.Button[Self]):
        await interaction.response.defer()
        self.stop()

        if interaction.message:
            await interaction.message.delete()

    @ui.button(emoji='\U000025b6', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: ui.Button[Self]):
        await interaction.response.defer()
        await self.show_checked_page(self.current_page + 1)  # type: ignore

    @ui.button(emoji='\U000023e9', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: ui.Button[Self]):
        await interaction.response.defer()
        await self.show_page(self._source.get_max_pages() - 1)
