import asyncio
import logging

import discord 

from discord import AllowedMentions 
from discord.ext import commands #NEED TO DELETE THIS AFTER DEVELOPMENT

from bot.constants import Logs, Rationals, Roles
from bot.bot import Bot
from bot.extension import load_all_extensions

log = logging.getLogger(__name__)
    
async def main():
    intents = discord.Intents.all()
    intents.members = True
    intents.presences = True
    intents.dm_typing = False
    intents.dm_reactions = False
    intents.invites = False
    intents.webhooks = False
    intents.integrations = False
    
    
    bot_ = Bot(
        command_prefix=("|"),
        case_insensitive=False,
        allowed_mentions=AllowedMentions(everyone=False),
        activity=discord.Game(name=f"Commands: {Rationals.prefix}help"),
        intents=intents
    )

    await load_all_extensions(bot_)
    await bot_.connection_pool()
    
    for func in bot_.helper_functions:
        func()
    
    await bot_.start(Rationals.token, reconnect=True)

asyncio.run(main())


            
        