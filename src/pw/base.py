from collections.abc import Sequence
from logging import getLogger
from os.path import join
from pathlib import Path
from random import randrange

from aiofiles import os as aos
from playwright.async_api import Error
from policy.captcha import captcha
from policy.connection import retry
from policy.exceptions import BrowserError, PageLoaded
from policy.login import Account
from settings import DATA_FOLDER, SESSION_FOLDER

logger = getLogger("buy-bot")

DEFAULT_NAVIGATION_TIMEOUT = 15000  # ms
DEFAULT_CONTEXT_TIMEOUT = 15000  # ms
# DEFAULT_TIMEOUT_FOR_PAGE_LOADING = 1000  # ms
DEFAULT_SHOULD_START_LOADING_IN = 1000  # ms

RESOURCE_EXCLUSTIONS = ['image', 'stylesheet', 'media', 'font', 'other']


def page_loaded(request):
    """
    Unhandaled page_loaded may mean that page was not loaded fully
    """
    raise PageLoaded(request.url)


class NoValidPage(Exception):
    pass


class NoValidContext(Exception):
    pass


class Playwright():
    # TODO:
    #   - Add graceful closing (partially done)
    #   - Optimize loading times - drop loading images (jpg, png etc.), minimize sleeps etc.
    #   - add full support for PGG - by hand captcha
    #   - add automatic captcha resolver or captcha workaround
    #   - add email notification
    #   - add storing and analysis of items properties - price trends availability etc.
    #   - improve logging, discord info
    def __init__(
            self, browser,
            login_username_field_locator, login_password_field_locator, login_submit_button_locator,
            account: Account,
            context=None, page=None, state_file_path=None,
            max_retries=None, retry_delay=None, retry_backoff=None,
            wait_until=None
    ):
        self.state_file_path = state_file_path or self._construct_default_state_file_path()
        self._context = context
        self._page = page
        self._browser = browser
        self.max_retries = 500 if max_retries is None else max_retries
        self.retry_delay = 5 if retry_delay is None else retry_delay
        self.retry_backoff = 0 if retry_backoff is None else retry_backoff
        self.wait_until = wait_until or "commit"
        self.login_username_field_locator = login_username_field_locator
        self.login_password_field_locator = login_password_field_locator
        self.login_submit_button_locator = login_submit_button_locator
        self.account = account

    def log_attr(self, *args):
        for attr in args:
            self.logger.debug(f"{attr}={getattr(self, attr)}")

    @property
    def username(self):
        return self.account.username

    @property
    def password(self):
        return self.account.password

    @property
    def pesel(self):
        return self.account.pesel

    @property
    def page(self):
        if self._page:
            return self._page
        else:
            self.logger.debug(f"No valid page: _page={self._page}")
            self.log_attr("_context", "_browser")

    @page.setter
    def page(self, value):
        self._page = value

    @property
    def context(self):
        if self._context:
            return self._context
        else:
            self.logger.debug(f"No valid context: _context={self._context}")
            self.log_attr("_page", "_browser")

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def browser(self):
        if self._browser:
            return self._browser
        else:
            self.logger.critical(f"_browser={self._browser}")
            self.log_attr("_page", "_context")

    def _construct_default_state_file_path(self):
        filename = f"{type(self).__name__}_{self.username}.json"
        path = join(DATA_FOLDER, SESSION_FOLDER)
        return join(path, filename)

    # @retry(error=UnrecoverableError)
    # async def start(self):
    #     try:
    #         await self.start_buy_out()
    #     except UnrecoverableError as e:
    #         self.logger.error(f"{type(e).__name__} '{e}' at start()")
    #         await self.close()
    #         raise UnrecoverableError
    #     except asyncio.CancelledError as e:
    #         self.logger.critical(f"{type(e).__name__} {e}")
    #         self.logger.warning("CTR+C detected")
    #         self.logger.info("Gracefully closing")
    #         await self.close()
    #         self.logger.info("Browser close end")
    #         raise

    async def close(self):
        self.logger.debug("Closing page")
        try:
            await self.page.close()
        except Error as e:
            self.logger.error(f"Couldn't close page due to {type(e).__name__} '{e}'")
        self.logger.debug(f"Trying to save context to {self.state_file_path}")
        try:
            await self.context.storage_state(path=self.state_file_path)
        except Error as e:
            self.logger.error(f"Couldn't save context due to {type(e).__name__} '{e}'")
        else:
            self.logger.info(f"State successfully stored at {self.state_file_path}")
        self.logger.debug("Closing context")
        try:
            await self.context.close()
        except Error as e:
            self.logger.error(f"Couldn't close context due to {type(e).__name__} '{e}'")
        self.logger.debug("Clearing page and context instance attributes")
        self.page = None
        self.context = None

    def _calc_delay(self):
        if isinstance(self.retry_delay, Sequence) and len(self.retry_delay) == 2:
            delay_s = randrange(*self.retry_delay)
        else:
            delay_s = self.retry_delay
        return delay_s

    async def _block_uneeded_resources(self):
        def route_abort_resources(route):
            if route.request().resourceType() in RESOURCE_EXCLUSTIONS:
                route.abort()
            else:
                getattr(route, "continue")

        # custom routing
        await self.page.route("**/*", route_abort_resources)


    # async def _reload_till_stable(self, max_reloads):
        # self.logger.debug(f"Attempting to recover trough repetitive reloads in {ERROR_DELAY_IN_S}s intervals")
        # reloads_left = max_reloads
        # while reloads_left >= 0:
            # reloads_left -= 1
            # await asyncio.sleep(ERROR_DELAY_IN_S)
            # self.logger.debug(f"Reload {max_reloads - reloads_left}/{max_reloads}")
            # try:
                # await self.page.reload(wait_until=self.wait_until)
            # except Error:
                # continue
            # else:
                # self.logger.debug("Page recovered!")
                # break
        # else:
            # self.logger.error(f"Could not recover through {max_reloads} page reloads")
            # raise UnrecoverableError

    async def ensure_context(self):
        if not self.context:
            await aos.makedirs(Path(self.state_file_path).parent, exist_ok=True)
            try:
                self.context = await self.browser.new_context(storage_state=self.state_file_path)
            except FileNotFoundError:
                self.logger.info(f"State was not found. File {self.state_file_path} does not exist")
                self.context = await self.browser.new_context()
            except Error:
                self.logger.critical("Browser is dead, we are doomed..")
                raise BrowserError
            else:
                self.logger.info(f"State successfully restored from {self.state_file_path}")
        self.context.set_default_timeout(DEFAULT_CONTEXT_TIMEOUT)
        self.context.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)

    async def ensure_page(self):
        if not self.page:
            self.page = await self.context.new_page()
        else:
            self.logger.info(f"Page already exist: {self.page}")
        self.page.set_default_timeout(DEFAULT_CONTEXT_TIMEOUT)
        self.page.set_default_navigation_timeout(DEFAULT_NAVIGATION_TIMEOUT)


    async def login(self):
        await self.page.fill(self.login_username_field_locator, self.username)
        await self.page.fill(self.login_password_field_locator, self.password)
        await self.page.click(self.login_submit_button_locator)

    @retry(max_retries=300)
    async def ensure_login(self):
        await self.page_goto(self.login_url)
        if self.page.url == self.login_url:
            await self.login()
            self.logger.info(f"Login to {self.login_url} successful")
        else:
            self.logger.info("Already logged in!")

    async def prepare_session(self):
        self.logger.info("Ensure context")
        await self.ensure_context()
        self.logger.info("Ensure page")
        await self.ensure_page()
        self.logger.info("Ensure login")
        await self.ensure_login()
        await self.context.storage_state(path=self.state_file_path)
        self.logger.info(f"State stored in {self.state_file_path}")

    @retry(max_retries=300)
    @captcha
    async def page_reload(self):
        async with self.page.expect_navigation(wait_until=self.wait_until):
            self.logger.debug("Page reload")
            await self.page.reload(wait_until=self.wait_until)
        self.logger.debug("Page reload with navigation done")

    @retry(max_retries=300)
    @captcha
    async def page_goto(self, url):
        # async with self.page.expect_navigation(wait_until=self.wait_until):
        self.logger.debug(f"Page executing {url}")
        await self.page.goto(url, wait_until=self.wait_until, timeout=DEFAULT_SHOULD_START_LOADING_IN)
        self.logger.debug("Page started loading")
