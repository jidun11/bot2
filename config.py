import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    startmsg = (
        "The bot is up and running. These bots "
        "can store messages in custom chats, "
        "and users access them through the bot."
    )
    forcemsg = (
        "To view messages shared by bots. "
        "Join first, then press the Try Again button."
    )

    API_ID = int(os.environ.get("API_ID", 2040))
    API_HASH = os.environ.get("API_HASH", "b18441a1ff607e10a989891a5462e627")
    OWNER_ID = int(os.environ.get("OWNER_ID", 487936750))
    MONGO_URL = os.environ.get("MONGO_URL", "mongodb://root:passwd@mongo")

    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    DATABASE_ID = int(os.environ.get("DATABASE_ID", ""))

    BOT_ID = BOT_TOKEN.split(":", 1)[0]


Config = Config()
