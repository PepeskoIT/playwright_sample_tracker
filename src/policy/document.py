from datetime import datetime
from functools import wraps
from logging import getLogger
from os.path import join

import aiofiles
from aiofiles import os as aos

from shop.definition import SHOP_FOLDERS, DATE_FORMAT

logger = getLogger("buy-bot")


async def dump_page(page, path, filename):
    await aos.makedirs(path, exist_ok=True)
    pic_full_path = join(path, f"{filename}.png")
    html_full_path = join(path, f"{filename}.html")
    await page.screenshot(
        path=pic_full_path
    )
    async with aiofiles.open(html_full_path, 'w') as s:
        await s.write(await page.content())


def document_page(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        self = args[0]
        date = str(datetime.utcnow().strftime(DATE_FORMAT))
        prefix_path = join(SHOP_FOLDERS[type(self).__name__], f.__name__)

        await dump_page(self.page, prefix_path, f"{date}_before")

        ret = await f(*args, **kwargs)

        await dump_page(self.page, prefix_path, f"{date}_after")
        return ret
    return decorated
