import logging
import typing as t
from datetime import datetime
from datetime import timezone

import discord
from discord.ext.commands import Context

from bot.db.connection import Tables

logger = logging.getLogger(__name__)

#icons
INFRACTIONS_ICONS = {}
INFRACTION_TYPES = ['warn', 'mute', 'pban', 'tempban', 'note']
INFRACTION_INFO = {
    'title': 'Please re-review our rules.',
    'name': 'Infraction Information', 
    'description':"""
        **Type**: {},\n
        **Expires**: {},\n
        **Reasons**: {}\n
    """
    
}

INFRACTION_BAN_FOOTER = "Please contact one of the admins regarding your infraction appeal."
INFRACTION_FOOTER = "Please contact ModMail regarding your infraction appeal."

MOD_LOG_INFO = """
    **Type**: {},\n
    **Actor**: {}, \n
    **Reason**: {}, \n
    **Expires**: {}
"""

def infraction_db(ctx):
    """Returns an instance of Table class."""
    return Tables('infractions', ctx.bot.pool)


async def post_infraction(
    ctx: Context, 
    user: discord.User, 
    infr_type: str, 
    reason:str = None,
    expires: datetime = None,
    ):  # sourcery skip: aware-datetime-for-utc
    """Uploads an infraction to the database."""
    
    if user.bot: 
        logger.info(f"Posting of {infr_type} infraction for {user} to the API aborted. User is a bot.")
        raise TypeError

    upload = {'user_id': user.id, 'type': infr_type, 'reason': reason, 'issued_time': datetime.utcnow(), 'active': True, 'actor': ctx.author.id} 
    upload['permanent'] = bool(expires)

    if not upload['permanent']:
        upload['expires'] = expires

    try:  
        await infraction_db(ctx).insert(**upload)
    except Exception as e:
        logger.exception(f"Unexpected error while adding user {user}")
        await ctx.send(':x: There was an error while adding infraction.')

async def get_active_infraction(
    ctx: Context, 
    user: discord.Member,
    infr_type: str, 
    send_message: bool = True,
    ):  
    """ 
    If the user has an active infraction matching the infraction type and 
    send message is True: It sends a message to the context channel informing the moderator.
    """
    logger.info(f"Checking if {user} has an active infraction with infraction type: {infr_type}")
    
    async with ctx.bot.db_connection as conn:
        active_infraction = await conn.fetch(
            'SELECT * FROM infraction WHERE user_id = $1 AND type = $2 AND active = $3',
            user.id, infr_type, True
        )
        
    if active_infraction:
        logger.info("{user} has an active infraction of {infr_type}")
        if send_message:
            infraction_type = infraction_db().from_dict('type', infraction_db().to_dict(active_infraction))
            await ctx.send(
                f"This user has an active infraction of infraction type: {infraction_type['type']}"
                f"See infraction: **#{infraction_type['id']}**"
                )
    else:
        logger.info("{user} does not have an active infraction {infr_type}")



async def notify_member(
    type_:str,
    user: discord.Member, 
    infraction_info:tuple = tuple, 
    ):
    """Notifies a user about their infraction or their pardon.""" 
    
    if type_ == 'infraction':
        logger.info(f"DMing {user} about their infraction.")

        infraction_text = INFRACTION_INFO["description"].format(*infraction_info)

        embed = discord.Embed(
            description=infraction_text, 
            colour = discord.Colour.dark_red() 
        )


        embed.set_author(name=INFRACTION_INFO["name"])
        embed.title = INFRACTION_INFO["title"]
        embed.set_footer(
            text=INFRACTION_BAN_FOOTER if 'ban' in infraction_info else INFRACTION_FOOTER
        )

    else:
        logger.info("DMing {user} about their infraction pardon")

        embed = discord.Embed(
            description="You have been unmuted.", 
            colour=discord.Colour.dark_green()
        )
        embed.set_author(title='Pardon')
        
    logger.info(f"Sending the dm to {user}")

    try:
        await user.send(embed=embed)
        return True
    except (discord.HTTPException, discord.Forbidden, discord.NotFound):
        logger.debug(
            f"Infraction-related information could not be sent to user {user} ({user.id}). "
            "The user either could not be retrieved or probably disabled their DMs."
        )
        return False
async def send_private_embed(user:t.Union[discord.User, discord.Member], embed: discord.Embed) -> bool:
    ...