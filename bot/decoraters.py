import typing as t
import logging

from discord.ext import commands

from bot.constants import STAFF_ROLES

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
        if not any(guild.get_role(role) in ctx.author.roles for role in items):
            logger.info(f'{str(ctx.author)} does not have the required roles. \
                role check failed.')
            return False
        logger.info(f'Bypassing role check for {str(ctx.author)}.')
        return True
