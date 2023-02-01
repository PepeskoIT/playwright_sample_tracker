from logging import getLogger
from os.path import join
from tempfile import TemporaryDirectory
from unittest.mock import patch, DEFAULT

import pytest
from playwright.async_api import Error, TimeoutError
from shop.tauron.tauron import TauronBuy
from tests.functional.tauron.test_data import ABS_FOLDER_PATH
from shop.accounts import ALL_TAURON_ACCOUNTS
from main import main

LOGIN_URL = join(ABS_FOLDER_PATH, "login.html")
PROD_IN_STOCK_URL = join(ABS_FOLDER_PATH, "a1.html")
CART_PAGE_URL = join(ABS_FOLDER_PATH, "aaa.html")
ORDER_STEP1_URL = join(ABS_FOLDER_PATH, "ddd.html")
ORDER_FINAL_STEP_URL = join(ABS_FOLDER_PATH, "final.html")


logger = getLogger("buy-bot")


async def dummy_send_to_my_discord(msg):
    logger.info(f"DISCORD EMULATOR: '{msg}'")


@patch('shop.base.send_msg_to_my_discord', dummy_send_to_my_discord)
@patch('policy.connection.send_msg_to_my_discord', dummy_send_to_my_discord)
async def test_main(get_chrome):
    sys_argv = [
        '', '-s', 'tauron', '-l', 'debug', '--gui',
    ]
    # inv = 0
    with TemporaryDirectory() as temp_dir:
        # temp_state_file = join(temp_dir, 'test_state')
        with patch('settings.DATA_FOLDER', temp_dir), patch('sys.argv', sys_argv):
            main()
