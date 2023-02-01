from shop.definition import LOGIN_ENDPOINT

DEFAULT_RETRY = (5, 10)

SHOP_URL = "https://sklep.tauron.pl"
CART_ENDPOINT = "/cart"
ORDER_CREATE_ENDPOINT = "/orders/create"

LOGIN_URL = f"{SHOP_URL}{LOGIN_ENDPOINT}"
CART_URL = f"{SHOP_URL}{CART_ENDPOINT}"
ORDER_URL = f"{SHOP_URL}{ORDER_CREATE_ENDPOINT}"

LOGIN_USERNAME_FIELD_LOCATOR = "#form_username"
LOGIN_PASSWORD_FIELD_LOCATOR = "#form_password"
LOGIN_SUBMIT_BUTTON_LOCATOR = "#id_zalogujsie_btn"

PRODUCTS_LOCATOR = "#page_products > div > div > div:nth-child(1) > div"  # only in bags = .col-lg-4
# PRODUCTS_LOCATOR = "#page_products .col-lg-4 .product"  # only in bags
PRODUCT_NAME_LOCATOR = "h3"
PRODUCT_PRICE_LOCATOR = "p.price.magenta > span"
PRODUCT_AVAILABILITY_LOCATOR = ".add"
PRODUCT_ADD_TO_CART_BUTTON = ".btn"
PRODUCT_NOT_AVAILABLE_TEXT = "niedostępny"
PRODUCT_QUANTITY_LOCATOR = "p:nth-child(10) > span"
PRODUCT_CATEGORY_LOCATOR = ".mt-10"

INIT_FORM_CLIENT_TYPE_LOCATOR = "#ff_legal_entity_id"
INIT_FORM_CLIENT_TYPE_LABEL = "Osoba fizyczna"  # value 1
INIT_FORM_EXCISE_TYPE_LOCATOR = "#excise_excemption_id"
INIT_FORM_EXCISE_TYPE_LABEL = "Gospodarstwo domowe - cel opałowy"  # value 1
INIT_FORM_DELIVERY_TYPE_LOCATOR = "#carrier-id-select"
INIT_FORM_DELIVERY_TYPE_LABEL = "Kurier"  # value 2
INIT_FORM_POSTAL_NUMBER_LOCATOR = "#postal-code-input"
INIT_FORM_POSTAL_NUMBER_VALUE = ""
INIT_FORM_CITY_LIST_LOCATOR = "#citylist"
INIT_FORM_CITY_LIST_LABEL = ""
INIT_FORM_SUBMIT_BUTTON_LOCATOR = "#button"
INIT_FORM_ERROR_BUTTON_LOCATOR = "body > div.swal2-container.swal2-fade.swal2-in > div > button.swal2-confirm.swal2-styled"

PRODUCT_ADD_QTY_BUTTON_LOCATOR = ".btn-plus" #"#add_to_cart > div > div > div > div:nth-child(2) > div:nth-child(1) > div.col-md-5.text-center > div.row.m-b > div.col-md-12.form-horizontal.text-center > div > span:nth-child(3) > button"
PRODUCT_VIEW_QTY_LOCATOR = ".input-quantity" #add_to_cart > div > div > div > div:nth-child(2) > div:nth-child(1) > div.col-md-5.text-center > div.row.m-b > div.col-md-12.form-horizontal.text-center > div > input
PRODUCT_ADD_TO_CARD_LOCATOR = "#add_button"
PRODUCT_ADDRESS_LOCATOR = "p.more > a"

CART_QTY_LOCATOR = "input.btn"
CART_ADD_QTY_BUTTON_LOCATOR = "button.btn-sm:nth-child(3)"
CART_SUBMIT_ORDER_BUTTON_LOCATOR = "a.btn:nth-child(2)"

ORDER_PESEL_LOCATOR = "#form_customer\[pesel\]"
ORDER_SUBMIT_STEP1_BUTTON_LOCATOR = "#id_submit_order_form"
ORDER_SUBMIT_STEP2_BUTTON_LOCATOR = "div.row:nth-child(14) > div:nth-child(3) > button:nth-child(1)"
ORDER_WIRE_TRANSFER_BUTTON_LOCATOR = ".payments > div:nth-child(4) > div:nth-child(1)"
ORDER_SUBMIT_STEP3_BUTTON_LOCATOR = "div.row:nth-child(7) > div:nth-child(3) > button:nth-child(1)"
ORDER_AGREEMENT_CHECKBOX_LOCATOR = "#form_summary\[order_conditions\]\[11\]"
ORDER_FINAL_SUBMIT_BUTTON_LOCATOR = "#create_order_button"


ALLOWED_PRODUCT_NAMES = ["EKOSOBIESKI", "TAURON"]

MAX_ITEM_QTY = 2
