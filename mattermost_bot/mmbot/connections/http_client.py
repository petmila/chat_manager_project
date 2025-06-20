import json
from typing import Optional
import aiohttp
from decouple import config


class HTTPSession:
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    def start(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def stop(self):
        await self._session.close()
        self._session = None

    async def get_chat_by_source_id(self, source_id) -> Optional[dict]:
        if self._session is None:
            self.start()
        async with self._session.get(url=config('CHAT_BY_SOURCE_URL') + f"by-source-id/{source_id}/",
                                     auth=aiohttp.BasicAuth(config('MATTERMOST_ADMIN_USER'),
                                                            config('MATTERMOST_ADMIN_PASSWORD')),
                                     ) as response:
            if response.status == 404:
                return None
            return await response.json()

    async def get_chats_by_nickname(self, nickname):
        if self._session is None:
            self.start()
        async with self._session.get(url=config('CHAT_URL') + f"by-nickname/{nickname}/",
                                     auth=aiohttp.BasicAuth(config('MATTERMOST_ADMIN_USER'),
                                                            config('MATTERMOST_ADMIN_PASSWORD')),
                                     ) as response:
            if response.status == 404:
                return None
            return await response.json()

    async def post_message(self, data):
        if self._session is None:
            self.start()
        async with self._session.post(url=config('MESSAGE_URL'),
                                      auth=aiohttp.BasicAuth(config('MATTERMOST_ADMIN_USER'),
                                                             config('MATTERMOST_ADMIN_PASSWORD')),
                                      data=json.dumps(data, default=str),
                                      headers={"Content-Type": "application/json"}) as response:
            return await response.json()