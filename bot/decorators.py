import asyncio
import typing as t
import logging

from discord.ext import commands

from bot.constants import Server, Channels

logger = logging.getLogger(__name__)

def channel_check(channel: t.Optional[int]=None, *bypass_roles:t.Tuple[int]) -> t.Callable:
    """Decorater responsible for checking if the user has the roles to use the
    command on that channel"""
    if not bypass_roles:
        bypass_roles = Server.staff_roles
    if not channel:
        channel = Channels.bot_commands
    async def wrapper(ctx: commands.Context) -> bool:
        """Check if the command was invoked in an allowed channel"""
        guild = ctx.guild
        member = ctx.author
        channel_to_check = guild.get_channel(channel)

        if ctx.channel != channel_to_check and all(guild.get_role(role) not in member.roles for role in bypass_roles):
            logger.info(
                f'Not allowing command ({ctx.command}) for {member} in channel {ctx.channel}'
            )

            return False
        else:
            logger.info(
                f'Bypassing channel check on command ({ctx.command}) for {member}.'
            )

            return True
        
    return commands.check(wrapper)

def redirect_output(channel:int, *bypass_roles:t.Tuple[int]) -> t.Callable:
    """Redirects the output of the command to the specified channel."""
    if not bypass_roles:
        bypass_roles = tuple(Server.staff_roles.values())
    if not channel:
        channel = Channels.bot_commands
        
    async def wrapper(ctx: commands.Context) -> True:
        """Redirecting the output.
        This returns True so that the command can send the message, None is falsey
        and will raise CheckFailure, and if checkfailure is raised the the command won't reach
        the sending part."""
        
        guild = ctx.guild
        if not guild.get_channel(channel):
            raise KeyError(f'Channel with id {channel} could not be found.')

        if any(x.id in bypass_roles for x in ctx.author.roles):
            logger.info(
                f'Bypassing on user {ctx.author} on redirecting the output of command {ctx.command}'
            )

            return True

        logger.info(f'Redirecting the output of {ctx.command} to {guild.get_channel(channel)}')
        redirect_message = await ctx.channel.send(f'{ctx.author.mention} You can find the output of your command in <#{channel}>')

        await asyncio.sleep(10)
        await redirect_message.delete()
        await ctx.message.delete()

        ctx.channel = guild.get_channel(channel) #overwriting ctx.channel to send the output to another channel.
        return True
        
    return commands.check(wrapper)

def role_check(required:bool, items: t.Tuple[int]) -> t.Callable:
    """
    Checks if the user:
    Either has any of the required roles: `required = False.` 
    Or has all of the required roles: `required = True.`
    """
    async def wrapper(ctx: commands.Context) -> bool:
        # sourcery skip: invert-any-all
        """Checks the role depending on the requirement."""
        guild = ctx.guild
        if required:
            if all(guild.get_role(role) not in ctx.author.roles for role in items):
                logger.info(f'{str(ctx.author)} does not have any of the disallowed roles')
                return True
            logger.info(f"The user {str(ctx.author)} has the disallowed role: {', '.join(guild.get_role(role) for role in items if guild.get_role(role) in ctx.author.roles)}")
            return False 
        else:
            if not any(guild.get_role(role) in ctx.author.roles for role in items):
                logger.info(f'{str(ctx.author)} does not have the required roles. \
                    role check failed.')
                return False
            logger.info(f'Bypassing role check for {str(ctx.author)}.')
            return True

    return commands.check(wrapper)