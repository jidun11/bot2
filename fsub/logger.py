import datetime
import logging


class Time:
    def __init__(self, offset: int) -> None:
        self.offset = offset

    def _offset_(self) -> datetime:
        utctime = datetime.datetime.utcnow()
        timeoffset = datetime.timedelta(hours=self.offset)
        return utctime + timeoffset

    def converted(self, *args) -> tuple:
        return self._offset_().timetuple()


WIBTime = Time(7)


class Logger:
    def __init__(self, __name__: str):
        self.name = __name__
        self.time = WIBTime
        self.setup()

    def setup(self) -> logging:
        logging.Formatter.converter = self.time.converted
        logging.basicConfig(
            format="%(asctime)s | %(levelname)s | %(name)s | " "%(message)s",
            datefmt="%b %d | %X",
            handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
            level=logging.INFO,
        )
        logging.getLogger("pyrogram").setLevel(logging.WARNING)
        logging.getLogger("pymongo").setLevel(logging.WARNING)
        self.log = logging.getLogger(self.name)


__Logger__ = Logger("Bot")
Logger = __Logger__.log
