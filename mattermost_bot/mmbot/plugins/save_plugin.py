import datetime
import re

from mmpy_bot import Plugin, listen_to, WebHookEvent, listen_webhook
from mmpy_bot import Message

from main import session, connection
from mmbot.decorators import listen_without_mention


class SavePlugin(Plugin):
    def __init__(self, bot_user_id, settings):
        super().__init__()
        self.bot_user_id = bot_user_id
        self.settings = settings

    @listen_without_mention(".*")
    async def save_messages(self, message: Message):
        # Проверка что чат не новый
        chat = await session.get_chat_by_source_id(message.channel_id)
        if chat is None:
            await self.export_chat_history(channel_id=message.channel_id)
        await self.format_message_for_updates_queue(message)

        print("saving message")
        # self.driver.reply_to(message, 'something')

    async def export_chat_history(self, channel_id: str):
        page = 0
        all_messages = []
        next_page_exists: bool = True
        while next_page_exists:
            posts = await self.driver.posts.get_posts_for_channel(
                channel_id,
                params={"page": page, "per_page": 100}
            )
            next_page_exists = posts["has_next"]
            order = posts.get("order", [])
            if not order:
                break
            for post_id in reversed(order):
                post = posts["posts"][post_id]
                all_messages.append(post)

            page += 1

        return all_messages

    async def format_message_for_updates_queue(self, message: Message):
        reply_id = message.reply_id if message.reply_id is not None else None
        data = {'text': message.text, 'timestamp': datetime.datetime.now(),
                'source_message_id': message.id,
                'reply_source_message_id': reply_id,
                'forward_from': None,
                'employee_account': {
                    'nickname': message.sender_name,
                    'source': 'Mattermost'},
                'chat': {
                    'source_chat_id': message.channel_id,
                    'chat_source': 'Mattermost',
                    'name': message.channel_name,
                }}
        connection.send_message(message=data, queue_name="updates_queue")