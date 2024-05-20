import asyncio
import logging
import logging.config
import hashlib
from database import db
from config import Config
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from pyrogram.enums import ParseMode
from pyrogram.errors import FloodWait

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

class Bot(Client):
    def __init__(self):
        # Hash the long session name to create a short unique identifier
        session_hash = hashlib.sha256(Config.BOT_SESSION.encode()).hexdigest()[:16]
        super().__init__(
            session_hash,  # Use the hashed session name
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins={
                "root": "plugins"
            },
            workers=50,
            bot_token=Config.BOT_TOKEN
        )
        self.log = logging

    async def start(self):
        await super().start()
        me = await self.get_me()
        logging.info(f"{me.first_name} with pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        self.id = me.id
        self.username = me.username
        self.first_name = me.first_name
        self.set_parse_mode(ParseMode.DEFAULT)
        text = "**๏[-ิ_•ิ]๏ bot restarted !**"
        logging.info(text)
        success = failed = 0
        users = await db.get_all_frwd()
        async for user in users:
           chat_id = user['user_id']
           try:
              await self.send_message(chat_id, text)
              success += 1
           except FloodWait as e:
              await asyncio.sleep(e.value + 1)
              await self.send_message(chat_id, text)
              success += 1
           except Exception:
              failed += 1 
        # await self.send_message("venombotsupport", text)
        if (success + failed) != 0:
           await db.rmve_frwd(all=True)
           logging.info(f"Restart message status: success: {success}, failed: {failed}")

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        logging.info(msg)

if __name__ == "__main__":
    app = Bot()
    app.run()
