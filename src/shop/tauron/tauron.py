from playwright.async_api import TimeoutError

from notify.discord_client import send_msg_to_my_discord
from policy.connection import retry
from policy.document import document_page
from shop.base import BasePwBuy
from shop.tauron import definitions

EXPECTED_CART_URL_PATTERN = f'**{definitions.CART_ENDPOINT}'
EXPECTED_ORDER_URL_PATTERN = f'**{definitions.ORDER_CREATE_ENDPOINT}*'


class TauronBuy(BasePwBuy):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            shop_url=definitions.SHOP_URL, login_url=definitions.LOGIN_URL,
            cart_url=definitions.CART_URL, order_url=definitions.ORDER_URL,

            login_username_field_locator=definitions.LOGIN_USERNAME_FIELD_LOCATOR,
            login_password_field_locator=definitions.LOGIN_PASSWORD_FIELD_LOCATOR,
            login_submit_button_locator=definitions.LOGIN_SUBMIT_BUTTON_LOCATOR,
            products_locator=definitions.PRODUCTS_LOCATOR,
            product_quantity_locator=definitions.PRODUCT_QUANTITY_LOCATOR,
            product_name_locator=definitions.PRODUCT_NAME_LOCATOR,
            product_price_locator=definitions.PRODUCT_PRICE_LOCATOR,
            product_availability_locator=definitions.PRODUCT_AVAILABILITY_LOCATOR,
            product_not_available_text=definitions.PRODUCT_NOT_AVAILABLE_TEXT,
            product_category_locator=definitions.PRODUCT_CATEGORY_LOCATOR,
            allowed_product_name=definitions.ALLOWED_PRODUCT_NAMES,
            max_retries=30, retry_delay=(5, 10), retry_backoff=0,
            **kwargs
        )

    @retry(max_retries=50)
    @document_page
    async def _ensure_excise_modal_appear(self, product_locator):
        normalized_url = self.page.url.strip("/")
        normalized_shop_url = self.shop_url.strip("/")
        if normalized_url not in normalized_shop_url:
            self.logger.warning(
                f"Page url != expected url:  {normalized_url}!={normalized_shop_url}. Manual page redirect"
            )
            await self.page_goto(self.shop_url)
        await product_locator.locator(definitions.PRODUCT_ADD_TO_CART_BUTTON).click(timeout=1000)
        self.logger.debug("Add to cart button clicked")
        await self.page.locator(definitions.INIT_FORM_CLIENT_TYPE_LOCATOR).wait_for(timeout=1000)
        self.logger.debug("Excise_modal form appeared")

    @retry(max_retries=300)
    @document_page
    async def _ensure_excise_modal_city_selected(self):
        await self.page.type(
            definitions.INIT_FORM_POSTAL_NUMBER_LOCATOR, definitions.INIT_FORM_POSTAL_NUMBER_VALUE
        )
        self.logger.info(f"Postal value was typed: {definitions.INIT_FORM_POSTAL_NUMBER_VALUE}")
        try:
            await self.page.select_option(
                f'select{definitions.INIT_FORM_CITY_LIST_LOCATOR}',
                label=definitions.INIT_FORM_CITY_LIST_LABEL, timeout=1000
            )
        except TimeoutError:
            self.logger.warning("Could not choose city for delivery within timeout")
            try:
                await self.page.click(definitions.INIT_FORM_ERROR_BUTTON_LOCATOR, timeout=1000)
            except TimeoutError:
                self.logger.warning("Warning button did not appear in time!")
            else:
                self.logger.debug("Warning button appeared and was clicked")
            finally:
                await self.page.fill(
                    definitions.INIT_FORM_POSTAL_NUMBER_LOCATOR, ""
                )
                self.logger.info("Postal-code cleared to reset city fetching")
                raise
        else:
            self.logger.info(f"City was selected, label={definitions.INIT_FORM_CITY_LIST_LABEL}")

    @retry(max_retries=50)
    async def _fill_excise_modal(self):
        # ExciseModal
        await self.page.select_option(
            f'select{definitions.INIT_FORM_CLIENT_TYPE_LOCATOR}',
            label=definitions.INIT_FORM_CLIENT_TYPE_LABEL
        )
        self.logger.info(f"Client type chosen, label={definitions.INIT_FORM_CLIENT_TYPE_LABEL}")
        await self.page.select_option(
            f'select{definitions.INIT_FORM_EXCISE_TYPE_LOCATOR}',
            label=definitions.INIT_FORM_EXCISE_TYPE_LABEL
        )
        self.logger.info(f"Excise type chosen, label={definitions.INIT_FORM_EXCISE_TYPE_LABEL}")
        await self.page.select_option(
            f'select{definitions.INIT_FORM_DELIVERY_TYPE_LOCATOR}',
            label=definitions.INIT_FORM_DELIVERY_TYPE_LABEL
        )
        self.logger.info(f"Delivery type chosen, label={definitions.INIT_FORM_DELIVERY_TYPE_LABEL}")
        await self._ensure_excise_modal_city_selected()
        ####
        async with self.page.expect_navigation(wait_until=self.wait_until, timeout=2500):
            await self.page.click(definitions.INIT_FORM_SUBMIT_BUTTON_LOCATOR)
            self.logger.info("Clicked submit button")
        self.logger.info("Product page loading")
        # redirect to product page

    @retry(max_retries=50)
    async def _ensure_qty_and_finalize_cart_add(self):
        # ProductPage
        # 1 is default value so 3 clicks give 4
        # TODO: check against already reported value
        await self.page.click(definitions.PRODUCT_ADD_QTY_BUTTON_LOCATOR, click_count=definitions.MAX_ITEM_QTY - 1)
        self.logger.info(f"Clicked QTY button {definitions.MAX_ITEM_QTY} times")
        # submit click changes url to cart ?? Dunno
        await self.page.click(definitions.PRODUCT_ADD_TO_CARD_LOCATOR)
        self.logger.info("Clicked 'add to cart'")
        await self.page.locator(".alert").wait_for()  # wait for message "Dodano towar do koszyka"
        self.logger.info("Detected 'added to cart' alert")

    @retry(max_retries=50)
    async def add_to_cart(self, product_locator):
        # product_url = await product_locator.locator(definitions.PRODUCT_ADDRESS_LOCATOR).get_attribute("href")
        await self._ensure_excise_modal_appear(product_locator)
        await self._fill_excise_modal()
        # product page
        await self._ensure_qty_and_finalize_cart_add()

    @retry(max_retries=200)
    async def checkout(self):
        await self.page_goto(self.cart_url)
        self.logger.info(f"At the cart page {self.cart_url}")
        await self.page.locator(definitions.CART_QTY_LOCATOR).wait_for()
        qty_in_cart = int(await self.page.locator(definitions.CART_QTY_LOCATOR).get_attribute("value"))
        self.logger.info(f"Detected QTY in the cart {qty_in_cart}")
        if not qty_in_cart == definitions.MAX_ITEM_QTY:
            self.logger.warning(f"QTY in cart != max item qty ({qty_in_cart}!={definitions.MAX_ITEM_QTY})")
            clicks_missing = definitions.MAX_ITEM_QTY - qty_in_cart
            await self.page.locator(definitions.CART_ADD_QTY_BUTTON_LOCATOR).click(click_count=clicks_missing)
            qty_in_cart = await self.page.locator(definitions.CART_QTY_LOCATOR).get_attribute("value")
            if not qty_in_cart == definitions.MAX_ITEM_QTY:
                self.logger.warning("Tried to adjust qty in cart but failed")
                self.logger.warning(f"QTY in cart != max item qty ({qty_in_cart}!={definitions.MAX_ITEM_QTY})")
        async with self.page.expect_navigation(wait_until=self.wait_until, timeout=2500):
            await self.page.locator(definitions.CART_SUBMIT_ORDER_BUTTON_LOCATOR).click()
            self.logger.debug("Clicked submit cart to checkout")
        self.logger.info("Loading new page")

    @retry(max_retries=50)
    async def _purchase_step_1(self):
        self.logger.info("Step1. Filling pesel")
        await self.page.fill(definitions.ORDER_PESEL_LOCATOR, self.pesel)
        await self.page.click(definitions.ORDER_SUBMIT_STEP1_BUTTON_LOCATOR)

    @retry(max_retries=50)
    async def _purchase_step_2(self):
        self.logger.info("Step2. Confirm cart")
        await self.page.click(definitions.ORDER_SUBMIT_STEP2_BUTTON_LOCATOR)

    @retry(max_retries=50)
    async def _purchase_step_3(self):
        self.logger.info("Step3. Choose payment")
        await self.page.click(definitions.ORDER_WIRE_TRANSFER_BUTTON_LOCATOR)
        await self.page.click(definitions.ORDER_SUBMIT_STEP3_BUTTON_LOCATOR)

    @retry(max_retries=50)
    async def _purchase_step_4(self):
        self.logger.info("Step4. Order finalization")
        await self.page.check(definitions.ORDER_AGREEMENT_CHECKBOX_LOCATOR)
        await self.page.click(definitions.ORDER_FINAL_SUBMIT_BUTTON_LOCATOR)

    @retry(max_retries=200)
    async def purchase(self):
        try:
            await self.page.wait_for_url(
                EXPECTED_ORDER_URL_PATTERN, timeout=1000, wait_until=self.wait_until
            )
        except TimeoutError:
            current_url = self.page.url
            self.logger.warning(
                f"Order page was not automatically loaded."
                f"Expected url: {EXPECTED_ORDER_URL_PATTERN}, got: {current_url}"
                f" Using direct {self.order_url} call"
            )
            await self.page_goto(self.order_url)
        else:
            current_url = self.page.url
            self.logger.debug(f"We are already in order page: {current_url}")
        await self._purchase_step_1()
        await self._purchase_step_2()
        await self._purchase_step_3()
        await self._purchase_step_4()
        self.logger.info("Purchase complete. Sending info via discord")
        await send_msg_to_my_discord("Purchase completed")
