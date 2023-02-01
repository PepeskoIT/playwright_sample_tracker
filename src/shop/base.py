import asyncio
from collections.abc import Sequence
from logging import getLogger

from notify.discord_client import send_msg_to_my_discord
from playwright.async_api._generated import Locator
from policy.connection import retry
from policy.exceptions import PageLoaded, UnrecoverableError
from policy.log import CustomAdapter
from pw.base import Playwright


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


class BasePwBuy(Playwright):
    def __init__(
            self,


            shop_url, login_url, cart_url, order_url,

            products_locator,  product_name_locator, product_price_locator,
            product_availability_locator, product_not_available_text,
            product_category_locator,

            allowed_product_category=None, allowed_product_name=None,
            log_adapter=None,
            products_locators=None, product_quantity_locator=None,
            captcha_locator=None, captcha_text=None, captcha_img_locator=None,
            **kwargs

    ):
        self.readable_id = type(self).__name__ + "_" + self.username

        self.logger = log_adapter or CustomAdapter(logger, type(self).__name__ + "_" + self.readable_id)

        self.shop_url = shop_url
        self.cart_url = cart_url
        self.login_url = login_url
        self.order_url = order_url

        self.products_locator = products_locator
        self.product_quantity_locator = product_quantity_locator
        self.product_name_locator = product_name_locator
        self.product_price_locator = product_price_locator
        self.product_availability_locator = product_availability_locator
        self.product_not_available_text = product_not_available_text
        self.product_category_locator = product_category_locator
        self.products_locators = products_locators

        self.allowed_product_category = allowed_product_category
        self.allowed_product_name = allowed_product_name

        self.captcha_locator = captcha_locator
        self.captcha_text = captcha_text
        self.captcha_img_locator = captcha_img_locator
        super().__init__(**kwargs)

    async def add_to_cart(self, product_locator=None):
        pass

    async def checkout(self):
        pass

    async def purchase(self):
        pass

    async def start_buy_out(self):
        self.logger.info("Prepare session")
        await self.prepare_session()
        while True:
            self.logger.info("Monitoring for items")
            product_locator = await self.monitor_items()
            self.logger.info("Adding items to cart")
            await self.add_to_cart(product_locator)
            self.logger.info("Checkout")
            await self.checkout()
            self.logger.info("Purchase")
            await self.purchase()
            self.logger.info("Buy-out complete!")

    @retry(error=UnrecoverableError)
    async def start(self):
        try:
            await self.start_buy_out()
        except UnrecoverableError as e:
            self.logger.error(f"{type(e).__name__} '{e}' at start()")
            await self.close()
            raise UnrecoverableError
        except asyncio.CancelledError as e:
            self.logger.critical(f"{type(e).__name__} {e}")
            self.logger.warning("CTR+C detected")
            self.logger.info("Gracefully closing")
            await self.close()
            self.logger.info("Browser close end")
            raise

    @retry(max_retries=50)
    async def monitor_items(self):
        self.logger.debug("Enter monitor items")
        await self.page_goto(self.shop_url)
        self.logger.info(f"At the page {self.page.url}. Starting to monitor.")
        while True:
            # page might still be loading
            if self.products_locator:
                products_locators = self.page.locator(self.products_locator)
                # TODO: parametrize me
                #   wait for first product at page to load = others will be available as-well
                await self.page.locator("div.element_3_on:nth-child(1) > div:nth-child(1)").wait_for()
                # elif self.products_locators:
                #     products_locators = [
                #         self.page.locator(p_locator)
                #         for p_locator in self.products_locators
                #     ]
            else:
                raise NotImplementedError
            available_product_locator = await self.is_desired_item_available(products_locators)
            if available_product_locator:
                return available_product_locator
            else:
                delay_in_s = self._calc_delay()
                self.logger.debug(f"Page reload in {delay_in_s}s")
                await asyncio.sleep(delay_in_s)
                await self.page_reload()
                continue

    async def is_desired_item_available(self, products_locators):
        available_products = []

        if isinstance(products_locators, Locator):
            get_prod_locator_f = "nth"
            products_cnt = await products_locators.count()
        elif isinstance(products_locators, Sequence):
            get_prod_locator_f = "pop"
            products_cnt = len(products_locators)
        else:
            raise NotImplementedError

        self.logger.debug(f"products_cnt: {products_cnt}")

        for i in range(products_cnt):
            product = getattr(products_locators, get_prod_locator_f)(i)
            product_name = (await product.locator(self.product_name_locator).text_content()).strip()
            self.logger.debug(f"product name: {product_name}")
            product_price = (await product.locator(self.product_price_locator).text_content()).strip()
            self.logger.debug(f"product price: {product_price}")
            product_category = (await product.locator(self.product_category_locator).text_content()).strip()
            self.logger.debug(f"product category: {product_category}")
            product_availability = (
                await product.locator(self.product_availability_locator).text_content()
            ).strip()
            self.logger.debug(f"product availability: {product_availability}")
            is_product_available = self.product_not_available_text.lower() not in product_availability.lower()
            if self.allowed_product_category:
                if not any(key in product_category for key in self.allowed_product_category):
                    continue
            if is_product_available:
                availability_msg = f"Product: {product_name}, price: {product_price}"
                if self.product_quantity_locator:
                    product_quantity = (
                        await product.locator(self.product_quantity_locator).text_content()
                    ).strip()
                    availability_msg += f" QTY: {product_quantity}"
                self.logger.info(availability_msg)
                await send_msg_to_my_discord(availability_msg)
                if self.allowed_product_name:
                    if not any(key in product_name for key in self.allowed_product_name):
                        self.logger.info(
                            f"{product_name} is available but NOT allowed - skip."
                            f"Allowed are {self.allowed_product_name}"
                        )
                        continue
                    available_products.append(product)
        return available_products[0] if available_products else None
