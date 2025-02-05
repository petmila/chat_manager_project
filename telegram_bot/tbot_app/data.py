import aiohttp
import json

from decouple import config


async def post_message(session, data):
    if session is None:
        session = aiohttp.ClientSession()
    async with session.post(url=config('MESSAGE_URL'),
                                    auth=aiohttp.BasicAuth(config('TELEGRAM_ADMIN_USER'), config('TELEGRAM_ADMIN_PASSWORD')),
                                    data=json.dumps(data, default=str),
                                    headers={"Content-Type": "application/json"}) as response:
        return await response.json()

async def post_summary(session, data):
    if session is None:
        session = aiohttp.ClientSession()
    async with session.post(url=config('SUMMARY_URL'),
                                    auth=aiohttp.BasicAuth(config('TELEGRAM_ADMIN_USER'), config('TELEGRAM_ADMIN_PASSWORD')),
                                    data=json.dumps(data, default=str),
                                    headers={"Content-Type": "application/json"}) as response:
        return await response.json()