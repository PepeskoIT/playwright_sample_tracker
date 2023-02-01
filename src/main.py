import argparse
import asyncio
import sys
from logging import getLogger

from playwright.async_api import Error
from playwright.async_api import async_playwright

from logging_setup import load_logger_config
from policy.exceptions import BrowserError
from shop.accounts import ALL_TAURON_ACCOUNTS, ALL_PGG_ACCOUNTS, ALL_MEDICOVER_ACCOUNTS
from shop.pgg.pgg import PggBuy
from shop.tauron.tauron import TauronBuy
from shop.medicover.medicover import MedicoverBuy

logger = getLogger("buy-bot")


SHOP_DATA = {
    "tauron": {"bot": TauronBuy, "accounts": ALL_TAURON_ACCOUNTS},
    "pgg": {"bot": PggBuy, "accounts": ALL_PGG_ACCOUNTS},
    "medicover": {"bot": MedicoverBuy, "accounts": ALL_MEDICOVER_ACCOUNTS}
}


def str_to_class(name):
    return getattr(sys.modules[__name__], name)


def get_tauron_account(username):
    for account in ALL_TAURON_ACCOUNTS:
        if account.username == username:
            return account


async def runner(shop, engine, gui: bool):
    bot_client = SHOP_DATA[shop]["bot"]

    async with async_playwright() as p:
        browser = await getattr(p, engine).launch(headless=not gui)

        all_clients = (bot_client(browser, account=account) for account in ALL_TAURON_ACCOUNTS)

        conf_fut = {
            asyncio.create_task(task.start(), name=task.readable_id)
            for task in all_clients
        }
        pending = conf_fut

        logger.debug("RUNNING JOBS!")
        while pending:
            finished, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_EXCEPTION)
            for task in finished:
                exception = task.exception()
                task_name = task.get_name()
                parts = task_name.split("_")
                shop = parts[0]
                user = parts[1]
                if exception:
                    logger.error(
                        f"Task '{task_name}' failed to execute. "
                        f"Got uncaught exception {type(exception).__name__} {exception}"
                    )
                    conf_fut.remove(task)
                    new_bot_client = bot_client(browser, account=get_tauron_account(user))
                    new_bot_client_id = new_bot_client.readable_id
                    new_task = asyncio.create_task(new_bot_client.start(), name=new_bot_client_id)
                    pending.add(new_task)
                    logger.info(f"Task {new_task} re-added to running tasks")

            logger.info(f"IN PROGRESS: {len(pending)}: {set(task.get_name() for task in pending)}")

        logger.info("No more pending jobs")


async def main():
    main_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Start bot at given shop'
        )
    )
    main_parser.add_argument(
        "-e", "--engine", type=str, required=False, help="engine to run", choices=["chromium", "firefox", "webkit"],
        default="chromium"
    )
    main_parser.add_argument(
        "-s", "--shop", type=str, required=False, help="shop to monitor", choices=["pgg", "tauron", "medicover"]
    )
    main_parser.add_argument(
        "--gui", action='store_true', required=False, help="start with gui"
    )
    main_parser.add_argument(
        "-l", "--log-level", type=str, required=False, help="log level", choices=["info", "debug"],
        default="info"
    )
    args = main_parser.parse_args()
    load_logger_config(level=args.log_level.upper())
    while True:
        try:
            await runner(args.shop, args.engine, args.gui)
        except (Exception, asyncio.CancelledError, Error, BrowserError) as e:
            logger.critical(f"Critical crash. {type(e).__name__} '{e}'")
            logger.info("Reload whole program")
        else:
            logger.info("Runner completed all jobs")
            break


try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("CLOSE")
