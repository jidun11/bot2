import asyncio
import contextlib
import time

from pyrogram.errors import FloodWait, RPCError
from pyrogram.filters import command, create, regex
from pyrogram.handlers import CallbackQueryHandler as Cbq
from pyrogram.handlers import MessageHandler as Msg
from pyrogram.helpers import ikb
from pyrogram.raw.functions import Ping
from pyrogram.types import CallbackQuery, Message

from bot import Bot

from .helpers import Markup, decorator, helpers

gVarBcRun = False
gVarBcSent = 0
gVarBcFail = 0
gVarBcTotal = 0


@decorator(["adminsOnly"])
async def broadcast(client: Bot, message: Message):
    async def progress(msg) -> Message:
        global gVarBcSent
        global gVarBcFail
        global gVarBcTotal

        with contextlib.suppress(RPCError):
            await msg.edit(
                f"Broadcast Status:\n - Sent: {gVarBcSent}/{gVarBcTotal}\n - Failed: {gVarBcFail}",
                reply_markup=ikb(Markup.BROADCAST_STATS),
            )

    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    if not (bcmsg := message.reply_to_message):
        return await message.reply("Reply to message.", quote=True)

    if gVarBcRun:
        return await message.reply("Currently broadcast is running.", quote=True)

    msg = await message.reply(
        "Broadcasting...", quote=True, reply_markup=ikb(Markup.BROADCAST_STATS)
    )

    await client.mdb.inmsg("bmsg", message.chat.id, msg.id)

    users = await client.mdb.gusrs()
    admns = helpers.adminids
    users = [usr for usr in users if usr not in admns]

    gVarBcRun = True
    gVarBcSent = 0
    gVarBcFail = 0
    gVarBcTotal = len(users)

    client.log.info("Starting Broadcast")
    for usr in users:
        if not gVarBcRun:
            break
        try:
            await helpers.copymsgs(bcmsg, usr)
            gVarBcSent += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            client.log.warning(str(e))
        except RPCError:
            await client.mdb.rmusr(usr)
            gVarBcFail += 1
        if gVarBcSent + gVarBcFail % 150 == 0:
            asyncio.create_task(progress(msg))

    if gVarBcSent + gVarBcFail == gVarBcTotal:
        await msg.delete()

    await message.reply(
        f"Sent: {gVarBcSent}/{gVarBcTotal}\nFailed: {gVarBcFail}",
        quote=True,
        reply_markup=ikb([[("Close", "home-close")]]),
    )

    gVarBcRun = False
    gVarBcSent = 0
    gVarBcFail = 0
    gVarBcTotal = 0

    client.log.info("Broadcast Finished")

    await client.mdb.rmmsg("bmsg")


async def cbqbcstats(client: Bot, cbq: CallbackQuery):
    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    data = cbq.data.split("-")[1]
    if data == "refresh":
        with contextlib.suppress(RPCError):
            await cbq.message.edit(
                f"Broadcast Status:\n - Sent: {gVarBcSent}/{gVarBcTotal}\n - Failed: {gVarBcFail}",
                reply_markup=ikb(Markup.BROADCAST_STATS),
            )
    elif data == "abort":
        await client.mdb.rmmsg("bmsg")
        gVarBcRun = False
        await cbq.message.edit(
            "Broadcast Aborted!", reply_markup=ikb([[("Close", "home-close")]])
        )


@decorator(["adminsOnly"])
async def cbqstats(client: Bot, cbq: CallbackQuery):
    global gVarBcRun
    global gVarBcSent
    global gVarBcFail
    global gVarBcTotal

    users = await client.mdb.gusrs()
    data = cbq.data.split("-")[1]
    if data == "ping":
        start = time.time()
        await client.invoke(Ping(ping_id=0))
        laten = f"{(time.time() - start) * 1000:.2f}ms"
        await cbq.answer(f"Pong! {laten}", show_alert=True)
    if data == "users":
        await cbq.answer(
            f"Total: {len(users)} Users",
            show_alert=True,
        )
    if data == "bc":
        if not gVarBcRun:
            return await cbq.answer("No Broadcast is Running!", show_alert=True)
        Broadcast = f"Broadcast Status:\n - Sent: {gVarBcSent}/{gVarBcTotal}\n - Failed: {gVarBcFail}"
        await cbq.answer(Broadcast, show_alert=True)


GROUP = create(lambda _, __, message: message.chat.type.value == "group")

Bot.hndlr(Msg(broadcast, filters=command(Bot.cmd.broadcast) & ~GROUP))
Bot.hndlr(Cbq(cbqbcstats, filters=regex(r"^bc")))
Bot.hndlr(Cbq(cbqstats, filters=regex(r"^stats")))
