import asyncio
import functools
import sys

from pyrogram.errors import RPCError
from pyrogram.types import BotCommand

from bot import Bot
from plugins import helpers, loadplugin


async def main():
    await dbctrl()

    Bot.log.info("Starting Client")
    await starting()

    Bot.log.info("Initializing DatabaseID")
    await getdbcid()
    Bot.log.info("DatabaseID Initialized")

    Bot.log.info("Fetching Mongo Database")
    await Bot.var.fetching()

    Bot.log.info("Initializing Environment")
    await helpers.cached()

    Bot.log.info("Setting Bot Command")
    await botcmd()

    Bot.log.info("Importing Plugins")
    loadplugin()

    Bot.log.info("Checking Restart Data")
    await rmsg("rmsg")
    await rmsg("bmsg")
    Bot.log.info("Restart Data Checked")


def rpchndlr(func):
    @functools.wraps(func)
    async def wrapper() -> callable:
        try:
            return await func()
        except RPCError as e:
            Bot.log.error(str(e))
            sys.exit(1)

    return wrapper


@rpchndlr
async def starting():
    await Bot.start()


@rpchndlr
async def getdbcid():
    hellomsg = await Bot.send_message(Bot.env.DATABASE_ID, "Hello Worldl!")
    await hellomsg.delete()


async def dbctrl():
    bvar = await Bot.mdb.gvars("BOT_VARS")
    dvar = {
        "GEN_STATUS": True,
        "PROTECT_CONTENT": True,
        "START_MESSAGE": Bot.env.startmsg,
        "FORCE_MESSAGE": Bot.env.forcemsg,
        "ADMIN_IDS": Bot.env.OWNER_ID,
    }
    if not bvar:
        for key, value in dvar.items():
            await Bot.mdb.invar("BOT_VARS", key, value)


async def botcmd():
    await Bot.set_bot_commands([BotCommand(Bot.cmd.start, "Starting Bot")])
    Bot.log.info("Bot Command Has Set")


async def rmsg(_id: str):
    rmsg = await Bot.mdb.gmsgs(_id)
    if rmsg:
        cid, mid = rmsg["cid"], rmsg["mid"]
        await Bot.send_message(cid, "Bot Restarted", reply_to_message_id=mid)
        await Bot.mdb.rmmsg(_id)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    Bot.log.info("Bot Has Been Activated")
    Bot.loop.run_forever()
