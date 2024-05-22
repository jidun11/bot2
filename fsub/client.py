import uvloop
from pyrogram import Client

from .config import Config
from .logger import Logger
from .utils import Cache, Commands, Database, URLSafe


class Bot(Client):
    def __init__(self):
        self.log = Logger
        self.env = Config
        self.var = Cache
        self.cmd = Commands
        self.url = URLSafe
        self.mdb = Database

        super().__init__(
            name=self.env.BOT_ID,
            api_id=self.env.API_ID,
            api_hash=self.env.API_HASH,
            bot_token=self.env.BOT_TOKEN,
            mongodb=dict(connection=self.mdb.Client, remove_peers=True),
        )

        self.hndlr = self.add_handler

    async def start(self):
        uvloop.install()
        await super().start()
        self.log.info(f"{self.me.id} Started")

    async def stop(self, *args):
        await super().stop()
        self.log.warning("Client Stopped")


Bot = Bot()
