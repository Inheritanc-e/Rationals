import yaml

import os

from collections import namedtuple


if not os.path.exists("default-config.yaml"):
    raise FileNotFoundError("File default-config.yaml does not exist.")

with open("default-config.yaml") as f:
    config = yaml.safe_load(f)

class StructuredDict:
    def __init__(self, args):
        for key, value in args.items():
            setattr(self, key, value)
            
Server = StructuredDict({
        "server_name": config['Server']['Name'],
        "server_id": config['Server']['ID'],
        "server_invite": config['Server']['Invite'],
        "staff_roles": tuple(value for key, value in config['Roles'].items() 
            if key in ['Founders', 'Admins', 'Moderators', 'Helpers']),
        "moderation_roles": tuple( value for key, value in config['Roles'].items() 
            if key in ['Founders', 'Admins', 'Moderators'])
})

Rationals = StructuredDict({
        "bot_name": config['Bot']['Name'],
        "bot_id": config['Bot']['ID'],
        "prefix": config['Bot']['Prefix'],
        "token": os.getenv("TOKEN")
})

Database = StructuredDict({
    "asyncpg_config": {
        "user": os.environ.get("DB_USER"),
        "database": os.environ.get("DB_NAME"),
        "host": os.environ.get("DB_HOST")
    }
})

Channels = namedtuple('Channels',list(config['Channels'].keys()), defaults=iter(config['Channels'].values()),) 

Staff_Channels = namedtuple('Staff_Channels', list(config['Staff_Channels'].keys()), defaults=iter(config['Staff_Channels'].values()))

Logs = namedtuple('Logs',list(config['Logs'].keys()), defaults=iter(config['Logs'].values()),)

Roles = namedtuple('Roles',list(config['Roles'].keys()), defaults=iter(config['Roles'].values()))