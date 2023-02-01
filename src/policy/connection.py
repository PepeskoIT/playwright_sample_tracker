import asyncio
from datetime import datetime
from functools import wraps
from logging import getLogger
from os.path import join

from playwright.async_api import Error

from notify.discord_client import send_msg_to_my_discord
from policy.document import dump_page, SHOP_FOLDERS, DATE_FORMAT
from policy.exceptions import UnrecoverableError, BrowserError

logger = getLogger("buy-bot")


def calc_loop(m_tries):
    if m_tries is None:
        return True
    else:
        return m_tries >= 1


def retry(error=Error, delay=False, max_retries=None, retry_backoff=None):
    def decorator(f):
        @wraps(f)
        async def decorated(*args, **kwargs):
            self = args[0]
            
            m_tries = max_retries
            m_backoff = retry_backoff

            last_exception = None
            last_exception_msg = None
            while calc_loop(m_tries):
                try:
                    return await f(*args, **kwargs)
                except error as e:
                    last_exception = e
                    # navigation and locator errors - diffrent actions
                    msg = f"{type(e).__name__} '{e}' during execution of {f.__name__}(args={args}, kwargs={kwargs})"
                    msg += f" while at page {self.page.url}. " if self.page else ". "
                    if m_tries is not None:
                        m_tries -= 1
                        msg += f"Retry {max_retries-m_tries}/{max_retries}"
                    self.logger.warning(msg)
                    last_exception_msg = msg
                    if str(e) == "Target page, context or browser has been closed":
                        self._check_core_attr("page", "context", "browser")
                        # TODO: check what failed - page, context or browser - test them somehow and recover if possible
                        raise BrowserError
                    if delay:
                        m_delay = self._calc_delay()
                        if m_backoff:
                            m_delay += m_backoff
                            m_backoff += m_backoff
                        self.logger.debug(f"Retry delay {m_delay} seconds")
                        await asyncio.sleep(m_delay)
                    else:
                        await asyncio.sleep(0.5)
            else:
                msg = (
                    f"All {max_retries} retries were used up. "
                    f"Dumping problematic page"
                )
                self.logger.critical(msg)
                date = str(datetime.utcnow().strftime(DATE_FORMAT))
                prefix_path = join(SHOP_FOLDERS[type(self).__name__], "error")
                prefix_filename = f"{date}_{type(last_exception).__name__}"
                try:
                    await dump_page(self.page, prefix_path, prefix_filename)
                except Error as e:
                    self.logger.error(f"Failed to dump page due to {type(e).__name__} '{e}'")
                else:
                    self.logger.debug(f"Page dumped into {join(prefix_path, prefix_filename)}")
                try:
                    await send_msg_to_my_discord(last_exception_msg)
                except Exception as e:
                    self.logger.error(f"Failed to send message via discord due to {type(e)} '{e}'")
                else:
                    self.logger.debug("Error information sent via discord")
                raise UnrecoverableError
        return decorated
    return decorator
