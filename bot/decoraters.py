import asyncio
import typing as t
import logging
import functools

from discord.ext import commands

from bot.constants import STAFF_ROLES
from bot.exceptions import NotThere

logger = logging.getLogger(__name__)


def channel_check(channel: int) -> t.Callable:
    """Decorater responsible for checking if the user has the roles to use the
    command on that channel"""
    async def wrapper(ctx: commands.Context) -> t.Boolean:
        """Check if the command was invoked in an allowed channel"""
        guild = ctx.guild
        channel_to_check = guild.get_channel(channel)
        if ctx.channel != channel_to_check and not any(guild.get_role(staff_role) for staff_role in STAFF_ROLES.values()):
            logger.info(f'{str(ctx.author)} does not have the required roles. \
                channel check failed!')
            return False
        logger.infof(f'Bypassing channel check for {str(ctx.author)}')
        return True
    return commands.check(wrapper)


def role_check(*items: t.Tuple[int]) -> t.Callable:
    """Checks if the user has any of the provided roles"""
    async def wrapper(ctx: commands.Context) -> bool:
        """Checking if the user has the specified role"""
        guild = ctx.guild
        if all(guild.get_role(role) not in ctx.author.roles for role in items):
            logger.info(f'{str(ctx.author)} does not have the required roles. \
                role check failed.')
            return False
        logger.info(f'Bypassing role check for {str(ctx.author)}.')
        return True
    return commands.check(wrapper)

def redirect_output(channel:int, *bypass_roles:t.Tuple[int]) -> t.Callable:
    """Redirects the output of the command to the specified channel."""
    async def wrapper(ctx: commands.Context) -> True: 
        """Redirecting the output.
        This returns True so that the command can send the message, None is falsey
        and will raise CheckFailure, and if checkfailure is raised the the command won't reach
        the sending part."""
        
        guild = ctx.guild
        if not guild.get_channel(channel):
            raise NotThere(f'Channel with id {channel} could not be found.')
        
        if any(x.id in bypass_roles for x in ctx.author.roles):
            logger.info(f'Bypassing on user {str(ctx.author)} on redirecting the output of command {ctx.command}')
            return True
        
        logger.info(f'Redirecting the output of {ctx.command} to {guild.get_channel(channel)}')
        redirect_message = await ctx.channel.send(f'{ctx.author.mention} You can find the output of your command in <#{channel}>')
        
        await asyncio.sleep(10)
        await redirect_message.delete()

        ctx.channel = guild.get_channel(channel) #overwriting ctx.channel to send the output to another channel.
        
        return True
        
    return commands.check(wrapper)
        