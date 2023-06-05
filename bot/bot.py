import datetime
import logging
 
import asyncpg
import discord
import aiohttp

from bot.constants import Channels, Logs, Rationals, Server, Database
from bot.db.connection import Connection
from bot.decorators import role_check

from discord.ext.commands import Bot as R

logger = logging.getLogger(__name__)

class Bot(R):
    """The core of the bot with some stuff"""
    
    def __init__(self, *a, **kw) -> None:
        """Setting the attributes for the bot"""
        super().__init__(*a, **kw)
        
        self.http_session = aiohttp.ClientSession()
        self.datetime = datetime.datetime
        self.start_time = datetime.datetime.now(datetime.timezone.utc)
        self.helper_functions = [self.hidden_commands]

    async def connection_pool(self):
        """Creates a connection pool and a `Connection` instance 
        which are used for transactions."""
        try:
            conn = await asyncpg.create_pool(**Database.asyncpg_config)
            self.pool = conn
            self.db_connection = Connection(conn)
        except Exception as e:
            logger.error(
                "Fialed to connect to postgres.",
                exc_info =(type(e), e, e.__traceback__)
            )
        finally:
            logger.info("Connected to postgres database.")

    async def on_ready(self) -> None:
        """A listerner which is invoked when the bot is ready"""
        logger.info(f'Successfully logged on as {self.user}')
        dev_log = self.get_channel(Channels().dev_log)
        
        prepare_embed = discord.Embed(description="Connected!", colour=discord.Color.dark_gold())
        prepare_embed.set_author(
            name=Rationals.bot_name.title(),
            url="https://github.com/Inheritanc-e/Rationals",
            icon_url=self.user.avatar.url
        )
        await dev_log.send(embed=prepare_embed)
            
    async def on_guild_available(self, guild:discord.Guild):
        """Check if there are required keys or roles in the
        server, any one of them seems to be missing 
        alert the admins, if there are no admins then send the message to the server owner
        """
        if guild.id != Server.server_id:
            return

        if not guild.roles and not guild.channels:
            logger.warning('Missing roles and channels!')
            await guild.owner.send('Missing roles, and channels in the server!')
            
            
    def hidden_commands(self):
        """
        Hides the commands which require `role_checks` check.
        `redirect_output` and `channel_checks` are exceptions.
        """
        commands_ = []
        for command in self.commands:
            commands_.extend(command for check in command.checks if role_check.__qualname__ in check.__qualname__)
        
        for cmd in commands_:
            cmd.hidden = True
    