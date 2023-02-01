from logging import getLogger

import aiohttp
from discord import Webhook, AsyncWebhookAdapter

from envs import DISCORD_TOKEN

logger = getLogger("buy-bot")

DISCORD_WEBHOOK = f"https://discord.com/api/webhooks/951612925905350666/{DISCORD_TOKEN}"


async def send_message_via_discord_webhook(url: str, msg: str):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        await webhook.send(msg, username='Spidey Bot')


async def send_msg_to_my_discord(msg: str):
    await send_message_via_discord_webhook(DISCORD_WEBHOOK, msg)
