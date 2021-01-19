import logging
import os
import yaml

# from dataclasses import dataclass
from typing import NamedTuple
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


class Getter(dict):
    """A getter class which allows dotted bheavior in dicts"""
    
    def __getattr__(self, key):
        """Allowing dotted bheavior."""
        return self[key]


class Server(NamedTuple):
    guild_id: int = config['Server']['ID']
    guild_name: str = config['Server']['Name']
    invite: str = config['Server']['Invite']


class Rationals(NamedTuple):
    name: str = config['Bot']['Name']
    id: int = config['Bot']['Id']
    prefix: str = config['Bot']['Prefix']
    token: str = os.getenv('TOKEN')


class Colour(Enum):
    ...


Channels = Getter(
    {channel.lower():channel_id for channel,channel_id in config['Channels'].items()
    if isinstance(channel_id, int)
    }
)


Logs = Getter(
    {channel.lower():channel_id for channel,channel_id in config['Channels']['Logs'].items()}
)


Help_System = Getter(
    {channel.lower():channel_id for channel, channel_id in config['Channels']['Help_System'].items()}
)


Roles = Getter(
    {role.lower():role_id for role, role_id in config['Roles'].items()}
)


Emojis = Getter(
    {k.lower():v for k,v in config['Emojis'].items()}
)

STAFF_ROLES = {
    role: role_id for role, role_id in config['Roles'].items()
    if role in ['Helpers', 'Moderators', 'Founders']
}
