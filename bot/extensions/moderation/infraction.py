import typing  as t
import logging 

import discord 

from discord.ext import commands
from discord.ext.commands import Context, command

from bot.constants import Server, Logs
from bot.extensions.moderation import utils
from bot.decorators import role_check

logger = logging.getLogger(__name__)
APPLIED_EMOJI = ":mailbox_with_mail: :ok_hand:"


class Infraction(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot 
        
    @command()
    @role_check(False, Server.moderation_roles)
    async def warn(self, ctx:Context, user:discord.User, *, reason:t.Optional[str]):
        """Warns an existing member for a given reason. """
        if isinstance(user, discord.ext.commands.Bot):
            await ctx.send("User is a bot. Aborting.")
            return
        
        await utils.post_infraction(ctx, user, 'warn', reason)
        await utils.notify_member('infraction', user, ('warn', 'N/A', reason))
        await ctx.send(f"{APPLIED_EMOJI} Applied warning to <@{user.id}> .")
    
    @command()
    @role_check(Server.moderation_roles, True)
    async def mute(self, ctx:Context, user:discord.User, *, reason:t.Optional[str]):
        """Mutes a member for the specified amount of time."""
        if isinstance(user, discord.ext.commands.Bot):
            await ctx.send("User is a bot. Aborting.")
            return
        
async def setup(bot: commands.Bot):
    """Loads the infraction cog"""
    await bot.add_cog(Infraction(bot)) 
    

        
        
        
