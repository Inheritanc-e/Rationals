import logging
import os
import yaml

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


if os.path.exists('bot/config/config.yaml'):
    logger.info('Found config.yaml loading the values from there.')

    with open('bot/config/config.yaml') as f:
        config = yaml.safe_load(f)
else:
    logger.info(
        'Could not find config.yaml trying to load the values from default-config.yaml!')

    with open('bot/config/config-default.yaml') as f:
        config = yaml.safe_load(f)


@dataclass
class Server:
    guild_id: int = config['Server']['ID']
    guild_name: str = config['Guild Name']
    invite: str = config['Server']['Invite']


@dataclass
class Rationals:
    name: str = config['Bot']['Name']
    id: int = config['Bot']['ID']
    prefix: str = config['Bot']['Prefix']
    token: str = os.getenv('TOKEN')


class Colour(Enum):
    ...


Channels = namedtuple(
    'Channels',
    [channel.lower() for channel in config['Channels'].keys()],  # type: ignore
    defaults=(
                channel for channel in config['Channels'].values()
                if isinstance(channel, int)
            ),
)

Logs = namedtuple(
    'Logs',
    [log.lower() for log in config['Channels']['Logs'].keys()],  # type: ignore
    defaults=(
        channel for channel in config['Channels']['Logs'].values()
        if isinstance(channel, int)
    ),

)

Help_System = namedtuple(
    'Help_System',
    [log.lower() for log in config['Channels']['Help_System'].keys()],  # type: ignore
    defaults=(
        channel for channel in config['Channels']['Logs'].values()
        if isinstance(channel, int)
    ),

)

Roles = namedtuple(
    'Roles',
    [role.lower() for role in config['Roles'].keys()],  # type: ignore
    defaults=iter(config['Roles'].values())
)


Emojis = namedtuple(
    'Emojis',
    [emoji.lower() for emoji in config['Emojis'].keys()],  # type: ignore
    defaults=iter(config['Emojis'].values())
)

STAFF_ROLES = {
    role: role_id for role, role_id in config['Roles'].items()
    if role in ['Helpers', 'Moderators', 'Founders']
}
