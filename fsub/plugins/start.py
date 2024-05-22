import asyncio

from pyrogram.errors import FloodWait, RPCError
from pyrogram.filters import command, private
from pyrogram.handlers import MessageHandler as Msg
from pyrogram.types import Message

from fsub import Bot

from .helpers import helpers


async def start(client: Bot, message: Message):
    user = message.from_user
    bttn = await helpers.usrikb(message, user.id)
    fnme = user.first_name
    full = f"{fnme} {user.last_name}".strip() if user.last_name else fnme
    ment = user.mention(full)

    await client.mdb.inusr(user.id)

    if len(message.command) == 1:
        if user.id in helpers.adminids:
            await message.reply(
                helpers.startmsg.format(first=fnme, full=full, mention=ment),
                reply_markup=helpers.admikb(),
            )
        else:
            await message.reply(
                helpers.startmsg.format(first=fnme, full=full, mention=ment),
                reply_markup=bttn,
            )
        return await message.delete()

    if await helpers.nojoin(user.id):
        await message.reply(
            helpers.forcemsg.format(first=fnme, full=full, mention=ment),
            reply_markup=bttn,
        )
        return await message.delete()

    mids = helpers.decode(message.command[1])
    for msg in await helpers.getmsgs(mids):
        try:
            await helpers.copymsgs(msg, user.id)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            client.log.warning(str(e))
        except RPCError:
            continue
    return await message.delete()


Bot.hndlr(Msg(start, filters=command(Bot.cmd.start) & private))
