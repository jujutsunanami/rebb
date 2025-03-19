#    This file is part of the AutoAnime distribution.

import asyncio


class Torrent:
    def __init__(self) -> None:
        self.cmd = """aria2c '''{link}''' -x 10 -j 10 --seed-time=0 -d '{path}'"""

    async def bash(self, cmd):
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        err = stderr.decode().strip() or None
        out = stdout.decode().strip()
        return out, err

    async def download_magnet(self, link: str, path: str):
        await self.bash(self.cmd.format(link=link, path=path))
