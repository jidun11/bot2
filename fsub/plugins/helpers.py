import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pyrogram.errors import RPCError
from pyrogram.helpers import ikb
from pyrogram.types import CallbackQuery, Message

from fsub import Bot


class Helpers:
    cacheids: Dict[str, Any] = {}
    protectc: bool = False
    generate: bool = False
    adminids: Optional[List[int]] = []
    fsubcids: Optional[List[int]] = []
    startmsg: Optional[str] = None
    forcemsg: Optional[str] = None

    def __init__(self, Client: Bot):
        self._client_ = Client

    def gvars(self, vari: str) -> Dict[str, Any]:
        return self._client_.var.vars.get(vari)

    def initializing(self):
        self.adminids = self.gvars("ADMIN_IDS")
        self._client_.log.info("Admins Initialized")
        self.fsubcids = self.gvars("FSUB_IDS")
        self.protectc = self.gvars("PROTECT_CONTENT")[0]
        self._client_.log.info(f"Protect {self.protectc}")
        self.startmsg = self.gvars("START_MESSAGE")[0]
        self._client_.log.info("Start Text Initialized")
        self.forcemsg = self.gvars("FORCE_MESSAGE")[0]
        self._client_.log.info("Force Text Initialized")
        self.generate = self.gvars("GEN_STATUS")[0]
        self._client_.log.info(f"Generate {self.generate}")

    def urlikb(self, text: str, url: str) -> ikb:
        return ikb([[(text, url, "url")]])

    def urlstr(self, url: str, share=False) -> str:
        if share:
            return f"https://t.me/share/url?url={url}"
        return "https://t.me/" f"{self._client_.me.username}?start={url}"

    def clear(self) -> Optional[Dict[str, Any]]:
        self.cacheids = {}

    def reload(self) -> Dict[str, Any]:
        self.clear()
        return self.initializing()

    async def cached(self) -> Dict[str, Any]:
        self.reload()
        if not self.fsubcids:
            return None
        for i, cid in enumerate(self.fsubcids):
            try:
                gchat = await self._client_.get_chat(cid)
                ctype = gchat.type.value
                title = "Group" if ctype in ["group", "supergroup"] else "Channel"
                ilink = gchat.invite_link
                self.cacheids[cid] = {
                    "title": title,
                    "ilink": ilink,
                }
                self._client_.log.info(f"FSubID-{i + 1} Initialized")
            except RPCError as e:
                self._client_.log.warning(f"FSubID-{i + 1}: {e}")

    async def usrikb(self, message: Message, user: int) -> Optional[ikb]:
        nojoin = await self.nojoin(user)
        if not self.fsubcids or not nojoin:
            return None
        buttons = []
        for cid in nojoin:
            title = self.cacheids[cid]["title"]
            ilink = self.cacheids[cid]["ilink"]
            buttons.append((f"Join {title}", ilink, "url"))
        layouts = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        if len(message.command) > 1:
            layouts.append([("Try Again", self.urlstr(message.command[1]), "url")])
        return ikb(layouts)

    async def nojoin(self, user: int) -> Optional[List[int]]:
        joined = set()
        if not self.fsubcids or user in self.adminids:
            return None
        for cid in self.fsubcids:
            try:
                await self._client_.get_chat_member(cid, user)
                joined.add(cid)
            except RPCError:
                continue
        return [cid for cid in self.fsubcids if cid not in joined]

    def encode(self, first: int, last: int) -> str:
        _data = first * abs(self._client_.env.DATABASE_ID)
        data_ = last * abs(self._client_.env.DATABASE_ID)
        return self._client_.url.encode(f"id-{_data}-{data_}")

    def decode(self, string: str) -> Union[List[int], range]:
        dbchid = self._client_.env.DATABASE_ID
        decoded = self._client_.url.decode(string).split("-")
        if len(decoded) == 2:
            return [int(int(decoded[1]) / abs(dbchid))]
        elif len(decoded) == 3:
            start = int(int(decoded[1]) / abs(dbchid))
            end = int(int(decoded[2]) / abs(dbchid))
            return range(start, end + 1) if start < end else range(start, end - 1, -1)

    async def getmsgs(self, ids: int) -> Optional[Message]:
        return await self._client_.get_messages(self._client_.env.DATABASE_ID, ids)

    async def copymsgs(self, msg: Message, user: int) -> Message:
        await msg.copy(user, protect_content=self.protectc)

    async def copymsg(self, msg: Message) -> int:
        copied = await msg.copy(
            self._client_.env.DATABASE_ID, disable_notification=True
        )
        return copied.id

    def admikb(self) -> List[List[Tuple[str, str]]]:
        buttons = []
        if self.fsubcids:
            for cid in self.fsubcids:
                title = self.cacheids[cid]["title"]
                ilink = self.cacheids[cid]["ilink"]
                buttons.append((title, ilink, "url"))
        layouts = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
        layouts.append([("Configuration", "home-home")])
        return ikb(layouts)


helpers = Helpers(Bot)


class Decorator:
    @staticmethod
    def admins(func: callable) -> Callable:
        @functools.wraps(func)
        async def wrapped(bot, event):
            user = Decorator.gusr(event)
            if user in helpers.adminids and isinstance(event, (Message, CallbackQuery)):
                await func(bot, event)

        return wrapped

    @staticmethod
    def gusr(event: Union[Message, CallbackQuery]) -> Optional[int]:
        if hasattr(event, "from_user"):
            return event.from_user.id
        if hasattr(event, "message") and hasattr(event.message, "chat"):
            return event.message.chat.id
        return -1

    def __call__(self, decors: List[str]) -> Callable:
        def decorator(func):
            if "adminsOnly" in decors:
                func = self.admins(func)
            return func

        return decorator


decorator = Decorator()


class Markup(List[List[Tuple[str, str]]]):
    HOME = [
        [("Generate Controller", "set-gen")],
        [("Start Text", "set-strtmsg"), ("Force Text", "set-frcmsg")],
        [("Protect Content", "set-prtctcntnt")],
        [("Admin IDs", "set-admnids"), ("FSub IDs", "set-fscids")],
        [("Stats", "home-stats"), ("Help", "home-help")],
        [("Close", "home-close")],
    ]

    STATS = [
        [("Broadcast", "stats-bc")],
        [("Ping", "stats-ping"), ("Users", "stats-users")],
        [("« Back", "home-home")],
    ]

    BACK = [[("« Back", "home-home")]]

    SET_ADMIN = [
        [("Add User", "add-admnids"), ("Del User", "del-admnids")],
        [("« Back", "home-home")],
    ]

    SET_FSUB = [
        [("Add Chat", "add-fscids"), ("Del Chat", "del-fscids")],
        [("« Back", "home-home")],
    ]

    SET_PROTECT = [[("« Back", "home-home"), ("Change", "change-prtctcntnt")]]

    SET_GENERATOR = [[("« Back", "home-home"), ("Change", "change-gen")]]

    SET_START = [[("« Back", "home-home"), ("Change", "change-strtmsg")]]

    SET_FORCE = [[("« Back", "home-home"), ("Change", "change-frcmsg")]]

    BROADCAST_STATS = [[("Stop", "bc-abort"), ("Ref.", "bc-refresh")]]


Markup = Markup()
