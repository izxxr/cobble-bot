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

from typing import List, Optional
from discord import app_commands
from tortoise import Tortoise
from core import utils, cosmetics
from discord.ext import commands
from discord.utils import MISSING
from core.checks import GenericError

import os
import logging
import discord

__all__ = (
    'CobbleBot',
)

_log = logging.getLogger()


class Config:
    """This class holds the configuration values for the bot."""
    def __init__(self) -> None:
        self.token: str = utils.get_config("COBBLE_BOT_TOKEN", MISSING)
        self.admin_ids: List[int] = [int(x) for x in utils.get_config("COBBLE_ADMIN_IDS", "").split(",")]
        self.debug_mode: bool = utils.get_config("COBBLE_DEBUG_MODE", False)
        self.debug_guild_id: Optional[int] = utils.get_config("COBBLE_GUILD_ID", None, factory=int)

class CobbleCommandTree(app_commands.CommandTree):
    """The app command tree."""
    async def on_error(  # type: ignore  # As always, Pyright is dumb.
            self,
            interaction: discord.Interaction[CobbleBot],
            error: app_commands.AppCommandError
        ) -> None:

        if isinstance(error, GenericError):
            await interaction.response.send_message(f'{cosmetics.EMOJI_ERROR} {error.message}')
        else:
            raise error


class CobbleBot(commands.Bot):
    """The cobble bot.
    
    Attributes
    ----------
    config: :class:`Config`
        The bot's configuration.
    """

    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or('?'),
            intents=discord.Intents(guilds=True, messages=True, message_content=True),
            description="A minecraft-inspired bot bringing fun survival experience to Discord servers.",
            allowed_mentions=discord.AllowedMentions(replied_user=True, everyone=False, users=False, roles=False),
            max_messages=None,
            tree_cls=CobbleCommandTree,
        )

        self.config: Config = MISSING

    async def launch(self) -> None:
        """Initializes and starts the bot.

        Raises a ValueError if COBBLE_BOT_TOKEN is not provided.
        """
        discord.utils.setup_logging()
        self.config = Config()

        if self.config.token is MISSING:
            raise ValueError('COBBLE_BOT_TOKEN environment variable missing')
        
        await self.start(self.config.token)

    async def on_ready(self) -> None:
        _log.info(f'Logged in and connected as {self.user} ({self.user.id})')  # type: ignore

    async def init_extensions(self, unload_all: bool = False, ignore_errors: bool = True) -> None:
        """Initializes the extensions from the cogs directory.

        If `unload_all` is set to True, any extensions already loaded are unloaded
        first. Note that files starting with an underscore are ignored.

        If `ignore_errors` is False, any extension loading error will be raised and
        remaining extensions will not be loaded. Otherwise, the error will be logged
        but the extensions loading will not be halted.
        """
        if unload_all:
            for extension in self.extensions:
                await self.unload_extension(extension)

        loaded = 0
        total = 0

        for filename in os.listdir('cogs'):
            if not filename.endswith('.py') or filename.startswith('_'):
                continue

            ext = filename[:-3]
            total += 1
            try:
                await self.load_extension(f'cogs.{ext}')
            except Exception:
                if not ignore_errors:
                    raise
                logging.error('An error occured while loading extension %r' % ext)
            else:
                loaded += 1

        logging.info(f'Loaded {loaded} extensions. {total - loaded} extensions could not be loaded.')


    async def init_database(self) -> None:
        await Tortoise.init(db_url='sqlite://db.sqlite3', modules=dict(models=['core.models']))  # type: ignore

    async def setup_hook(self) -> None:
        await self.init_extensions()
        await self.init_database()