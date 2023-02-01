from shop.definition import LOGIN_ENDPOINT

SHOP_URL = "https://sklep.pgg.pl"
CART_ENDPOINT = "/koszyk"
ORDER_ENDPOINT = "/zamowienia"

LOGIN_URL = f"{SHOP_URL}{LOGIN_ENDPOINT}"
CART_URL = f"{SHOP_URL}{CART_ENDPOINT}"
ORDER_URL = f"{SHOP_URL}{ORDER_ENDPOINT}"

LOGIN_USER_FIELD_ID = "email"
LOGIN_PASSWORD_FIELD_ID = "password"
LOGIN_BUTTON_TEXT = (' Zaloguj                                    ')
ADD_TO_CART_TEXT = (' Dodaj do koszyka                ')

PRODUCT_AVAILABILITY_LOCATOR = '[abt="Produkt jest dostępny"]'
PRODUCT_LOCATOR = '.produkt-box-container'
PRODUCT_PRICE_LOCATOR = 'div:nth-child(3) > div:nth-child(1) > ins:nth-child(1)'
PRODUCTS_LOCATOR = '.shop > div:nth-child(1) > div'
PRODUCTS_LOCATORS = ['\s+Pieklorz Ekogroszek\s+']
PRODUCT_NAME_LOCATOR = '.product-name'
PRODUCT_NOT_AVAILABLE_TEXT = "Chwilowy"
PRODUCT_CATEGORY_LOCATOR = '.product-category'
CAPTCHA_LOCATOR = 'body > b:nth-child(5)'
CAPTCHA_TEXT = "Przepisz kod widoczny na obrazku :"
CAPTCHA_IMG_LOCATOR = "body > img:nth-child(2)"

ALLOWED_PRODUCT_CATEGORY = ["Paleta"]

INPUT_ITEM_COUNT_LOCATOR = "input[name=ilosc]"

ADD_TO_CART_LOCATOR = f"text='{ADD_TO_CART_TEXT}'"

LOGIN_USERNAME_FIELD_LOCATOR = f'input[id="{LOGIN_USER_FIELD_ID}"]'
LOGIN_PASSWORD_FIELD_LOCATOR = f'input[id="{LOGIN_PASSWORD_FIELD_ID}"]'
LOGIN_SUBMIT_BUTTON_LOCATOR = f"text='{LOGIN_BUTTON_TEXT}'"

BUY_CNT = "2"
