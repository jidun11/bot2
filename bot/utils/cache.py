from bot.utils.db import Database
from bot.utils.logger import Logger
from config import Config


class Cache:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.data = None

    async def fetching(self) -> dict:
        self.clear()
        await self.relown()
        self.data = await self.gvars()
        Logger.info("Mongo Database Fetched")

    def clear(self) -> None:
        self.data = None

    async def gvars(self) -> dict:
        return await self.db.gvars("BOT_VARS")

    async def admnvar(self) -> None:
        bvars = await self.gvars()
        return bvars.get("ADMIN_IDS", [])

    async def relown(self) -> None:
        owner = Config.OWNER_ID
        admns = await self.admnvar()
        if owner not in admns:
            await self.db.invar("BOT_VARS", "ADMIN_IDS", owner)

    @property
    def vars(self) -> dict:
        return self.data


Cache = Cache(Database)
