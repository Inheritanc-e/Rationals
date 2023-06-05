import logging
import typing as t

from difflib import SequenceMatcher

import discord

from discord.ext import commands
from discord.ext.commands import errors

from bot.constants import Channels

logger = logging.getLogger(__name__)

class ErrorHandler(commands.Cog):
    """ 
    An error handler cog that handles all the errors emitted from commands and relays 
    the message to the dev channel.
    """

    def __init__(self,bot):
        self.bot = bot
        
    async def error_embed(self, ctx:commands.Context, cause:str, error:t.Union[str, errors.CommandError]):
        """Prepares and embed containing the error."""
        e = discord.Embed(
            title=f"{cause} occured.", 
            colour = discord.Colour.red(),
            description = error
        )
        e.set_footer(text=ctx.bot.datetime.utcnow().isoformat())
        return e
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, e:commands.CommandError):
        """
        Provides error handling. 
        """
        self.e = e
        debug_message = f"{ctx.command} invoked by {ctx.message.author} with error. \n {e.__class__.__name__}: {e}"
        print(debug_message)

        if isinstance(e, errors.UserInputError):
            logger.error(debug_message)
            await self.handle_user_input(ctx) 
        elif isinstance(e, errors.CheckFailure):
            logger.error(debug_message)
            await self.handle_check_failure(ctx)
        elif isinstance(e, errors.CommandOnCooldown):
            logger.error(debug_message)
            await ctx.send(e)
        elif isinstance(e, errors.CommandInvokeError):
            logger.error(debug_message)
            await self.send_command_help(ctx)
        elif isinstance(e, errors.CommandNotFound):
            logger.error(debug_message)
            await self.send_command_suggestion(ctx)
        else:
            logger.error(debug_message)
            await self.handle_unexpected_error(ctx)
    
    async def handle_user_input(self, ctx:commands.Context):
        """Handles the errors caused due to user input""" 
        if isinstance(self.e, errors.MissingRequiredArgument):
            embed = await self.error_embed(ctx, 'MissingRequiredArgument', self.e)
        elif isinstance(self.e, errors.TooManyArguments):
            embed = await self.error_embed(ctx, 'TooManyArguments',self.e)
        elif isinstance(self.e, errors.BadArgument):
            embed = await  self.error_embed(ctx, 'BadArgument', self.e) 
        elif isinstance(self.e, errors.BadUnionArgument):
            embed = await self.error_embed(ctx, 'BadUnionArgument', self.e)
        elif isinstance(self.e, errors.ArgumentParsingError):
            embed = await  self.error_embed(ctx, 'ArgumentParsingError', str(self.e))
            await ctx.send(embed=embed)
            return 
        else:
            embed = await self.error_embed(ctx, 'InputError', 'Unknown')
            
        await ctx.send(embed=embed)
        await self.send_command_help(ctx)
        
    async def send_command_suggestion(self, ctx:commands.Context):
        """Tries to find commands having similar syntax and sends those as suggestions."""
        raw_commands = [(cmd.name, *cmd.aliases) for cmd in ctx.bot.commands]
        command_name = ctx.invoked_with
        match = [
            command[0] for command in raw_commands 
            if any(round(SequenceMatcher(lambda x: x == ' ', command_name, item).ratio(), 3) > 0.6 
                                                                                for item in command)]
        if not match:
            logger.info("No similar command found.")
            return
        for matched_command in match:
            try:
                cmd = ctx.bot.get_command(matched_command)
                await cmd.can_run(ctx)
            except errors.CheckFailure as cmd_error:
                logger.info("Not sending command suggestions due to check failure.")
                self.e = cmd_error
                await self.handle_check_failure(ctx)
                return
        
        embed = discord.Embed(
            title = "Did you mean: ", 
            colour = discord.Colour.orange(), 
            description = "\n".join(f"• {m}" for m in match) + "\n :grey_question:"
        )
        await ctx.send(embed=embed, delete_after=10.0)
        

    async def handle_check_failure(self, ctx:commands.Context):
        """Handles errors caused due to check failure"""
        if isinstance(self.e, errors.CheckFailure):
            await ctx.send("Sorry, it looks like you don't have the required roles to perform this command.")
        elif isinstance(self.e, errors.BotMissingPermissions):
            await ctx.send("Sorry, it looks like I don't have the required permissions to perform this command.")
        elif isinstance(self.e, errors.NoPrivateMessage):
            await ctx.send("The given command cannot be performed in private messages.")
        
        
    async def handle_unexpected_error(self, ctx:commands.Context):
        """Handles unforseen errors."""
        await ctx.send(
            f"Sorry, an unexpected error occurred. Please let us know!\n\n"
            f"```{self.e.__class__.__name__}: {self.e}```"
        )
        logger.error(f"Error executing command invoked by {ctx.message.author}: {ctx.message.content}", exc_info=self.e)
        error_description = {
            "User_ID": ctx.author.id, 
            "User_Name": ctx.author.name, 
            "Command": ctx.command.qualified_name, 
            "Message_ID": ctx.message.id, 
            "Channel_ID": ctx.channel.id
        }
        error_info = discord.Embed(
            title = f"Unexpected error in {ctx.channel}", 
            colour = discord.Colour.dark_red(),
            description = "\n".join(f"{key}:{value}" for key, value in error_description.items())
        )
        guild = ctx.guild 
        dev_log = guild.get_channel(Channels.dev_log)
        await dev_log.send(embed=error_info)
        
   
    async def send_command_help(self, ctx:commands.Context):
        """Sends the help for the command invoked."""
        await ctx.send_help(ctx.command)



async def setup(bot: commands.Bot):
    """Loads the infraction cog"""
    await bot.add_cog(ErrorHandler(bot)) 