import pytest
from playwright.async_api import async_playwright

from logging_setup import load_logger_config

load_logger_config("/tmp")


@pytest.fixture()
async def get_chrome():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        yield browser
        await browser.close()


@pytest.fixture()
async def get_firefox():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        yield browser
        await browser.close()


@pytest.fixture()
async def get_webkit():
    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=False)
        yield browser
        await browser.close()


async def get_browser(name):
    async with async_playwright() as p:
        browser = await getattr(p, name).launch(headless=False)
        yield browser
        await browser.close()
