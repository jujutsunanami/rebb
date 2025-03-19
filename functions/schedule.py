# License can be found in <


import json
import os
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from functions.config import Var
from functions.info import AnimeInfo
from functions.tools import Tools
from libs.logger import LOGS, TelegramClient


class ScheduleTasks:
    def __init__(self, bot: TelegramClient):
        self.tools = Tools()
        self.bot = bot
        if Var.SEND_SCHEDULE or Var.RESTART_EVERDAY:
            self.sch = AsyncIOScheduler(timezone="Asia/Kolkata")
            if Var.SEND_SCHEDULE:
                self.sch.add_job(
                    self.anime_timing, "cron", hour=0, minute=30
                )  # 12:30 AM IST
            if Var.RESTART_EVERDAY:
                self.sch.add_job(self.restart, "cron", hour=2, minute=1)  # 2:01 AM IST
            self.sch.start()

    async def anime_timing(self):
        try:
            _res = await self.tools.async_searcher(
                "https://subsplease.org/api/?f=schedule&h=true&tz=Asia/Kolkata"
            )
            xx = json.loads(_res)
            xxx = xx["schedule"]
            text = "**📆 Anime AirTime Today** `[IST]`\n\n"
            for i in xxx:
                info = AnimeInfo(i["title"])
                text += f'`[{i["time"]}]` -  [{(await info.get_english())}](https://subsplease.org/shows/{i["page"]})\n'
            mssg = await self.bot.send_message(Var.MAIN_CHANNEL, text)
            await mssg.pin(notify=True)
        except Exception as error:
            LOGS.error(str(error))

    def restart(self):
        os.execl(sys.executable, sys.executable, "bot.py")
