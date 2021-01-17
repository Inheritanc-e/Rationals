import os
import logging
import logging.handlers


from pathlib import Path

try:
    os.mkdir(f'{Path.cwd()}/bot/logs')
except FileExistsError:
    pass
with open(f'{Path.cwd()}/bot/logs/bot.log', 'w') as f:
    pass

bot_logs = f'{Path.cwd()}/bot/logs/bot.log'


ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)

formatter = formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.handlers.RotatingFileHandler(
    bot_logs, maxBytes=25000000, backupCount=5
)

ch.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(ch)
