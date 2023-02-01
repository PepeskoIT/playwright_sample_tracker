from logging import getLogger
from os.path import join
from tempfile import TemporaryDirectory
from unittest.mock import patch, DEFAULT

import pytest
from playwright.async_api import Error, TimeoutError
from shop.tauron.tauron import TauronBuy
from tests.functional.tauron.test_data import ABS_FOLDER_PATH
from shop.accounts import ALL_TAURON_ACCOUNTS

LOGIN_URL = join(ABS_FOLDER_PATH, "login.html")
PROD_IN_STOCK_URL = join(ABS_FOLDER_PATH, "a1.html")
CART_PAGE_URL = join(ABS_FOLDER_PATH, "aaa.html")
ORDER_STEP1_URL = join(ABS_FOLDER_PATH, "ddd.html")
ORDER_FINAL_STEP_URL = join(ABS_FOLDER_PATH, "final.html")


logger = getLogger("buy-bot")


async def dummy_send_to_my_discord(msg):
    logger.info(f"DISCORD EMULATOR: '{msg}'")


class FinishTest(Exception):
    pass


@patch('shop.tauron.tauron.definitions.SHOP_URL', f"file://{PROD_IN_STOCK_URL}")
@patch('shop.tauron.tauron.definitions.CART_URL', f"file://{CART_PAGE_URL}")
@patch('shop.tauron.tauron.EXPECTED_CART_URL_PATTERN', "**aaa.html*")
@patch('shop.tauron.tauron.definitions.LOGIN_URL', f"file://{LOGIN_URL}")
@patch('shop.tauron.tauron.definitions.ORDER_URL', f"file://{ORDER_STEP1_URL}")
@patch('shop.tauron.tauron.EXPECTED_ORDER_URL_PATTERN', "**ddd.html*")
@patch('shop.tauron.tauron.send_msg_to_my_discord', dummy_send_to_my_discord)
@patch('shop.base.send_msg_to_my_discord', dummy_send_to_my_discord)
@patch('policy.connection.send_msg_to_my_discord', dummy_send_to_my_discord)
async def test_start_buy_out_loop(get_chrome):
    inv = 0
    with TemporaryDirectory() as temp_dir:
        temp_state_file = join(temp_dir, 'test_state')
        with patch('settings.DATA_FOLDER', temp_dir):
            for account in ALL_TAURON_ACCOUNTS:
                shop_client = TauronBuy(get_chrome, account=account, state_file_path=temp_state_file)
                ori_monitor_items = shop_client.monitor_items

                async def side_effect(*args, **kwargs):
                    nonlocal inv
                    if inv >= 2:
                        raise FinishTest
                    ret = await ori_monitor_items(*args, **kwargs)
                    inv += 1
                    return ret

                with patch.object(shop_client, "monitor_items") as mocked_monitor_items:
                    mocked_monitor_items.side_effect = side_effect
                    with pytest.raises(FinishTest):
                        await shop_client.start_buy_out()
    assert inv == 2


@patch('shop.base.send_msg_to_my_discord', dummy_send_to_my_discord)
@patch('shop.tauron.tauron.send_msg_to_my_discord', dummy_send_to_my_discord)
@patch('policy.connection.send_msg_to_my_discord', dummy_send_to_my_discord)
async def test_unrecoverable_error_handling(get_chrome):
    inv = 0
    with TemporaryDirectory() as temp_dir:
        temp_state_file = join(temp_dir, 'test_state')
        with patch('settings.DATA_FOLDER', temp_dir):
            shop_client = TauronBuy(get_chrome, account=ALL_TAURON_ACCOUNTS[0], state_file_path=temp_state_file)
            await shop_client.ensure_context()
            await shop_client.ensure_page()
            with patch.multiple(shop_client.page, goto=DEFAULT, reload=DEFAULT) as mocks:
                mocks["goto"].side_effect = TimeoutError("Test error")
                mocks["reload"].side_effect = TimeoutError("Test error")
                await shop_client.start()
    assert inv == 2


# @patch('shop.base.send_msg_to_my_discord', dummy_send_to_my_discord)
# @patch('shop.tauron.tauron.send_msg_to_my_discord', dummy_send_to_my_discord)
# @patch('policy.connection.send_msg_to_my_discord', dummy_send_to_my_discord)
# async def test_unrecoverable_error_handling(get_chrome):
#     inv = 0
#     with TemporaryDirectory() as temp_dir:
#         temp_state_file = join(temp_dir, 'test_state')
#         with patch('settings.DATA_FOLDER', temp_dir):
#             shop_client = TauronBuy(get_chrome, account=ALL_TAURON_ACCOUNTS[0], state_file_path=temp_state_file)
#             await shop_client.ensure_context()
#             await shop_client.ensure_page()
#             with patch.multiple(shop_client.page, goto=DEFAULT, reload=DEFAULT) as mocks:
#                 mocks["goto"].side_effect = TimeoutError("Test error")
#                 mocks["reload"].side_effect = TimeoutError("Test error")
#                 await shop_client.start()
#     assert inv == 2
