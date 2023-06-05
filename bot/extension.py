import os
import inspect
import typing as t
import importlib
import logging

log = logging.getLogger(__name__)


def get_files() -> t.Dict[str, str]:
    """Prepares all the files that are in bot/exts"""
    folders = list(list(os.walk('bot/extensions'))[0][1])
    dirs = {}

    # creating a dictonary which contains a list of all the files and subfiles
    # which contain .py in that folder

    for f in folders:
        for sf in list(os.walk(f'bot/extensions/{f}')):
            if '__pycache__'not in sf[0] and '__init__.cpython-38.pyc' not in sf[2]: 
                dirs[sf[0]] = sf[2]

    return dirs


def statement(dir: t.Dict[str, str]) -> t.Generator:
    """Prepares the statement which have to be executed. """
    for k, v in dir.items():
        for value in v:
            if '.py' not in value:
                continue

            # remove the `.py` from the name
            yield f"{k.replace('/', '.')}.{value[:len(value)-3]}"


def qualify_extension(statements) -> t.Set:
    """Returns only the set of modules that actually have cogs
    """
    Extensions = {'jishaku'}
    for module in statements:
        imported = importlib.import_module(module)
        if hasattr(imported, 'setup') and inspect.isfunction(getattr(imported, 'setup')):
            Extensions.add(module)

    return Extensions

EXTENSIONS = qualify_extension(statement(get_files()))

async def load_all_extensions(bot):
    if not EXTENSIONS:
        log.warning('Could not find any extensions!')
    else:
        for extension in EXTENSIONS:
            await bot.load_extension(extension)
        log.info(f"Loaded Extension {extension}")

    log.info("All extensions successfully!")