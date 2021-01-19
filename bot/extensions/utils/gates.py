import logging

import discord
from discord.ext import commands

from bot.constants import Channels, Logs

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = f"""
**Hello, and welcome to The Rationals.**

Thanks for accepting our rules. You can re-read them at <#758619609925550086>. 

Additionally, if you'd like to receive notifications for the announcements we post in <#{Channels.announcements}>
you can send `|notify` in <#{Channels.bot_commands} at any time to assign yourself the Announcements role.

If you'd like to unsubscribe from the notifications, simply send `|unnotify` in <#{Channels.bot_commands}>
"""


class Gates(commands.Cog):
    """Cog responsible for handling all the gating system of the server."""
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        
    @commands.Cog.listener('on_member_join')
    async def user_join(self, member: discord.Member) -> None:
        """Welcome the user when they join the server and send a message to
        user log channels.""" 
        user_log = member.guild.get_channel(Logs.user_log)       
        
        user_created = member.created_at.strftime("%d %B, %Y")
        user_joined = member.joined_at.strftime("%d %B, %Y")
        
        user_information = discord.Embed(title='User Information', description=f"""
                                         **Name** - {str(member)}
                                         **Joined** - {user_joined}
                                         **Created** - {user_created}""", 
                                         colour=discord.Color.red())
        
        user_information.set_author(name=str(member), icon_url=member.avatar_url)
        await user_log.send(embed=user_information)
        
        try:
            await member.send(WELCOME_MESSAGE)
        except discord.Forbidden:
            await user_log.send(f'Sending the message to {member.mention} \
                failed.')
        else:
            await user_log.send(f'Sending the message to {member.mention} \
                was successfull.')
            
    
def setup(bot):
    bot.add_cog(Gates(bot))
    
        
    
