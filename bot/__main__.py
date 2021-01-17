import logging
import discord

from discord import AllowedMentions

from bot.extension import EXTENSIONS
from bot.constants import Rationals
from bot.bot import Bot

log = logging.getLogger(__name__)


intents = discord.Intents.all()
intents.dm_typing = False
intents.dm_reactions = False
intents.invites = False
intents.webhooks = False
intents.integrations = False


bot = Bot(
    command_prefix=("|"),
    case_insensitive=False,
    allowed_mentions=AllowedMentions(everyone=False),
    activity=discord.Game(name=f"Commands: {Rationals.prefix}help"),
    intents=intents
)

if not EXTENSIONS:
    log.warning('Could not find any extensions!')
else:
    for extension in EXTENSIONS:
        bot.load_extension(extension)
        log.info(f"Loaded Extension {extension}")

    log.info("All extensions successfully!")

bot.run(Rationals.token, reconnect=True)
