import logging
import asyncio
import datetime

import aiohttp
import discord

from discord.ext.commands import Bot as R
from discord import Embed

from bot.constants import Channels, Rationals, Server

log = logging.getLogger(__name__)


class Bot(R):

    """The core of the bot with some stuff"""

    def __init__(self, *a, **kw) -> None:
        """Setting the attributes for the bot"""
        super().__init__(*a, **kw)

        self.http_session = aiohttp.ClientSession()

        self.loop = asyncio.get_event_loop()

        self.start_time = datetime.datetime.utcnow()

    async def on_ready(self) -> None:
        """A listerner which is invoked when the bot is ready
        """
        log.info(f'Successfully logged on as {self.user}')
        dev_log = self.get_channel(Channels().dev_log)

        prepare_embed = Embed(description="Connected!",
                              colour=discord.Color.blurple())
        prepare_embed.set_author(
            name=Rationals.name.title(),
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            icon_url=self.user.avatar_url
        )

        await dev_log.send(embed=prepare_embed)

    async def on_guild_available(self, guild: discord.Guild):
        """Check if there are required keys or roles in the server, any one of
        them seems to be missing alert the admins, if there are no admins then
        send the message to the server owner.
        """
        if guild.id != Server.guild_id:
            return

        if not guild.roles and not guild.channels:
            log.warning("Missing roles and channels!")
            await guild.owner.send("Missing roles and channels in the server!")

        # we are gonna add required keys check later for this event

    async def close(self) -> None:
        """Subclassing the logout command to ensure connection(s) are closed
        properly."""
        await asyncio.wait_for(self.http_session.close(), 30.0, loop=self.loop)

        log.info("Finished up closing task(s).")

        return await super().close()
