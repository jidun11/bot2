from pyrogram.filters import command, private
from pyrogram.handlers import MessageHandler as Msg
from pyrogram.helpers import ikb
from pyrogram.types import Message

from fsub import Bot

from .helpers import decorator, helpers


@decorator(["adminsOnly"])
async def generate(client: Bot, message: Message):
    if not helpers.generate:
        return None

    dbchid = client.env.DATABASE_ID
    copied = await helpers.copymsg(message)
    encode = client.url.encode(f"id-{copied * abs(dbchid)}")
    urlstr = helpers.urlstr(encode)
    urlmsg = f"https://t.me/c/{str(dbchid)[4:]}/{copied}"
    markup = ikb(
        [
            [
                ("Message", urlmsg, "url"),
                ("Share", helpers.urlstr(urlstr, share=True), "url"),
            ]
        ]
    )
    await message.reply(urlstr, reply_markup=markup)
    return await message.delete()


Bot.hndlr(Msg(generate, filters=~command(Bot.cmd.cmds) & private))
