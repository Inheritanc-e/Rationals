import contextlib
import os
import logging
import logging.handlers

from pathlib import Path

with contextlib.suppress(FileExistsError):
    os.mkdir(f'{Path.cwd()}/bot/logs')

bot_log = f"{Path.cwd()}/bot/logs/bot.log"

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.handlers.RotatingFileHandler(
    bot_log, maxBytes=25000000, backupCount=5
)

ch.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(ch)

    