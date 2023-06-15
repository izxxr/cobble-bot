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
from discord import app_commands
from core.models import Player

if TYPE_CHECKING:
    from core.bot import CobbleBot
    from discord import Interaction

__all__ = (
    'GenericError',
    'has_survival_profile',
    'cooldown_factory',
)


class GenericError(app_commands.AppCommandError):
    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message = message


def has_survival_profile():
    """Check to ensure that the user running a command has a survival profile."""
    async def predicate(interaction: Interaction) -> bool:
        profile = await Player.filter(id=interaction.user.id).first()
        if profile:
            interaction.extras["survival_profile"] = profile
            return True

        raise GenericError('No survival profile created yet. Use `/profile start` to create one.')

    return app_commands.check(predicate)


def cooldown_factory(rate: float, per: float, *, bypass_admin: bool = True):
    def predicate(interaction: Interaction[CobbleBot]) -> Optional[app_commands.Cooldown]:
        if bypass_admin and interaction.user.id in interaction.client.config.admin_ids:
            return None

        return app_commands.Cooldown(rate, per)

    return predicate
