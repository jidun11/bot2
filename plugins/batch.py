import contextlib
from typing import Optional

from pyrogram.filters import command, private
from pyrogram.handlers import MessageHandler as Msg
from pyrogram.helpers import ikb
from pyrogram.types import Message

from bot import Bot

from .helpers import decorator, helpers


@decorator(["adminsOnly"])
async def batch(client: Bot, message: Message):
    cid = message.chat.id
    uid = message.from_user.id
    cdb = client.env.DATABASE_ID

    async def ask(text: str, link: str) -> Optional[Message]:
        cask = await client.ask(
            chat_id=cid,
            text=text,
            user_id=uid,
            reply_markup=helpers.urlikb("Database", link),
        )
        await cask.sent_message.delete()
        if not cask.forward_from_chat or cask.forward_from_chat.id != cdb:
            await cask.reply("Invalid!", quote=True)
            return None
        return cask

    def dburl(msgid) -> str:
        return f"https://t.me/c/{str(cdb)[4:]}/{msgid}"

    await message.delete()

    fask = await ask(
        "Forward: First Message",
        f"tg://openmessage?chat_id={str(cdb)[4:]}",
    )
    if not fask:
        return
    first = fask.forward_from_message_id
    flink = dburl(first)
    await fask.delete()

    lask = await ask("Forward: Last Message", flink)
    if not lask:
        return
    last = lask.forward_from_message_id
    lurl = dburl(last)
    await lask.delete()

    with contextlib.suppress(ValueError):
        if (abs(int(first) - int(last)) + 1) > 200:
            return await message.reply("Can't retrieve >200 messages.")

    urlstr = helpers.urlstr(helpers.encode(first, last))
    markup = ikb(
        [
            [
                ("First", flink, "url"),
                ("Share", helpers.urlstr(urlstr, share=True), "url"),
                ("Last", lurl, "url"),
            ],
        ]
    )
    await message.reply(urlstr, reply_markup=markup)


Bot.hndlr(Msg(batch, filters=command(Bot.cmd.batch) & private))
