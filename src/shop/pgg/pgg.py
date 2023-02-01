import asyncio

from playwright.async_api import Error

from notify.discord_client import send_msg_to_my_discord
from policy.connection import retry
from policy.document import document_page
from shop.base import BasePwBuy
from shop.pgg import definitions


class PggBuy(BasePwBuy):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            shop_url=definitions.SHOP_URL, login_url=definitions.LOGIN_URL, cart_url=definitions.CART_URL,
            order_url=definitions.ORDER_URL,

            login_username_field_locator=definitions.LOGIN_USERNAME_FIELD_LOCATOR,
            login_password_field_locator=definitions.LOGIN_PASSWORD_FIELD_LOCATOR,
            login_submit_button_locator=definitions.LOGIN_SUBMIT_BUTTON_LOCATOR,
            products_locator=definitions.PRODUCTS_LOCATOR,
            product_name_locator=definitions.PRODUCT_NAME_LOCATOR,
            product_price_locator=definitions.PRODUCT_PRICE_LOCATOR,
            product_availability_locator=definitions.PRODUCT_AVAILABILITY_LOCATOR,
            product_not_available_text=definitions.PRODUCT_NOT_AVAILABLE_TEXT,
            products_locators=definitions.PRODUCTS_LOCATORS,
            product_category_locator=definitions.PRODUCT_CATEGORY_LOCATOR,
            allowed_product_category=definitions.ALLOWED_PRODUCT_CATEGORY,
            max_retries=10, retry_delay=(10, 15), retry_backoff=2,
            captcha_locator=definitions.CAPTCHA_LOCATOR, captcha_text=definitions.CAPTCHA_TEXT,
            captcha_img_locator=definitions.CAPTCHA_IMG_LOCATOR,
            **kwargs
        )

    @retry()
    @document_page
    async def add_to_cart(self, product_locator=None):
        if product_locator:
            await product_locator.locator(definitions.INPUT_ITEM_COUNT_LOCATOR).fill(definitions.BUY_CNT)
        else:
            await self.page.locator(definitions.INPUT_ITEM_COUNT_LOCATOR).fill(definitions.BUY_CNT)
        add_to_cart_locator = product_locator.locator(definitions.ADD_TO_CART_LOCATOR)
        is_disabled = (await add_to_cart_locator.get_attribute("disabled")) == "disabled"
        if is_disabled:
            msg = "Add to cart button is DISABLED"
            raise Error(msg)
        else:
            self.logger.info("Add to cart button is ENABLED")
        await add_to_cart_locator.click()

    @retry()
    @document_page
    async def checkout(self):
        while True:
            page_url = await self.page.url()
            if page_url not in self.cart_url:
                self.logger.warning(f"Cart page was not loaded automatically. Instead got {page_url}")
                await self.page_goto(self.cart_url)
                continue
            break
        await self.page.check('#akcyza_0')
        await self.page.check('#transport4')
        await self.page.click(
            '#main > div.shop-cart > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > button'
        )

    @retry()
    @document_page
    async def purchase(self):
        # TODO: finish purchase
        await send_msg_to_my_discord(f"Added to cart. Finish purchase - {definitions.CART_URL}")
        while True:
            await asyncio.sleep(100)
        # TODO: finish checkout
