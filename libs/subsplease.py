#    This file is part of the Anime distribution.

import asyncio
import hashlib
import shutil
import sys
from itertools import count
from traceback import format_exc

import anitopy
from feedparser import parse

from database import LOGS, DataBase


class SubsPlease:
    def __init__(self, dB: DataBase):
        self.db = dB

    def digest(self, string: str):
        return hashlib.sha256(string.encode()).hexdigest()

    def _exit(self):
        LOGS.info("Stopping The Bot...")
        try:
            [shutil.rmtree(fold) for fold in ["downloads", "thumbs", "encode"]]
        except BaseException:
            LOGS.error(format_exc())
        sys.exit(0)

    def rss_feed_data(self):
        try:
            return (
                parse("https://subsplease.org/rss/?r=1080"),
                parse("https://subsplease.org/rss/?r=720"),
                parse("https://subsplease.org/rss/?r=sd"),
            )
        except KeyboardInterrupt:
            self._exit()
        except BaseException:
            LOGS.error(format_exc())
            return None, None, None

    async def feed_optimizer(self):
        d1080, d720, d480 = self.rss_feed_data()
        if not d1080 or not d720 or not d480:
            return None
        for i in range(2, -1, -1):
            try:
                f1080, f720, f480 = d1080.entries[i], d720.entries[i], d480.entries[i]
                a1080, a720, a480 = (
                    (anitopy.parse(f1080.title)).get("anime_title"),
                    (anitopy.parse(f720.title)).get("anime_title"),
                    (anitopy.parse(f480.title)).get("anime_title"),
                )
                if a1080 == a720 == a480:
                    if (
                        "[Batch]" in f1080.title
                        or "[Batch]" in f720.title
                        or "[Batch]" in f480.title
                    ):
                        continue
                    uid = self.digest(f1080.title + f720.title + f480.title)
                    if not await self.db.is_anime_uploaded(uid):
                        return {"uid": uid, "1080p": f1080, "720p": f720, "480p": f480}
            except BaseException:
                LOGS.error(format_exc())
                return None

    async def on_new_anime(self, function):
        for i in count():
            data = await self.feed_optimizer()
            if data:
                await function(data)
                await self.db.add_anime(data.get("uid"))
            await asyncio.sleep(5)
