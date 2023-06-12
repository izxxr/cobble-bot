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
from typing_extensions import Self
from discord.interactions import Interaction
from discord import ui, ButtonStyle
from core import cosmetics

if TYPE_CHECKING:
    from discord.abc import Snowflake
    from discord import Interaction

__all__ = (
    'Confirmation',
)


class Confirmation(ui.View):
    def __init__(self, *, timeout: Optional[float] = 180, user: Snowflake):
        super().__init__(timeout=timeout)

        self.confirmed: Optional[bool] = None
        self.user = user

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(f'{cosmetics.EMOJI_ERROR} You cannot interact with this!')
            return False

        return True

    @ui.button(label='Confirm', style=ButtonStyle.green)
    async def confirm_button(self, interaction: Interaction, button: ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.confirmed = True
        self.stop()

    @ui.button(label='Cancel', style=ButtonStyle.gray)
    async def cancel_button(self, interaction: Interaction, button: ui.Button[Self]) -> None:
        await interaction.response.defer()
        self.confirmed = False
        self.stop()
