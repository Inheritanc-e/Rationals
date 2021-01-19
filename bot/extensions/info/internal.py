import traceback
import textwrap
import io
import re

from contextlib import redirect_stdout

import discord
from discord.ext import commands


from bot.exceptions import NotThere


# to expose to the eval command
import datetime
from collections import Counter


class Internal(commands.Cog):
    """SOme internal stuff"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def python_parser(self, code_input):
        """parses the code input and returns the actual code"""
        needed = ['```py', '```']
        if any(x not in code_input for x in needed):
            raise NotThere("```py and ``` are not in code input")

        starting_point = re.compile(r'\`\`\`py')
        result = str(re.search(starting_point, code_input))
        indexes = list(
            map(int, result[result.index('s')+6:result.index(')')].split(',')))

        end_point = re.compile(r'\`\`\`')
        raw_code = code_input[indexes[1]:]
        result2 = str(re.search(end_point, raw_code))
        indexes2 = list(
            map(int, result2[result2.index('s')+6:result2.index(')')].split(',')))

        return raw_code[:indexes2[0]]

    @commands.group(name='internal', aliases=['int'], hidden=True, invoke_without_command=True)
    async def internal(self, ctx) -> None:
        """The main grop command for internal stuff,
        this returns all the commands that internal group 
        has
        """

        message_to_send = discord.Embed(
            title='Internal', description="The list of some internal commands for the bot!", colour=discord.Colour.green())
        group = self.bot.get_command('internal')
        subcommands = "".join(
            f'\n ➼{x}. \n **Can also do**: int {" or  ".join(aliases for aliases in x.aliases)} \n' for x in group.walk_commands())
        fields = [
            ('Sub Commands', subcommands, False)
        ]

        for name, value, _ in fields:
            message_to_send.add_field(name=name, value=value, inline=False)

        await ctx.channel.send(embed=message_to_send)

    @internal.group(name='eval', aliases=['e'], hidden=True)
    async def internal_eval(self, ctx, *, code: str) -> None:
        """Eval the input code, and send the outputput in a formatted 
        manner
        """
        if ctx.author.id != 707472976454483988:
            return

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.python_parser(code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```cmd\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Internal(bot))
