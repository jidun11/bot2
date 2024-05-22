from typing import Any, Dict, Optional

from ..config import Config
from ..logger import Logger
from .db import Database


class Cache:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.data: Optional[Dict[str, Any]] = None

    async def fetching(self) -> Dict[str, Any]:
        self.clear()
        await self.relown()
        self.data = await self.gvars()
        Logger.info("Mongo Database Fetched")

    def clear(self) -> None:
        self.data = None

    async def gvars(self) -> Dict[str, Any]:
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
    def vars(self) -> Dict[str, Any]:
        return self.data


Cache = Cache(Database)
