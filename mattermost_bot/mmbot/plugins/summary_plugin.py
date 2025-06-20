import json
import re

from mmpy_bot import Plugin, listen_to, WebHookEvent, listen_webhook
from mmpy_bot import Message
import requests
from main import session
from mmbot.data.data_formatting import Keyboard, Button, Dialog, Element, Option


class SummaryPlugin(Plugin):
    def __init__(self, bot_user_id, settings):
        super().__init__()
        self.bot_user_id = bot_user_id
        self.settings = settings
        self.generation_options = [Option(text="Today", value="now(\"-1d\")"),
                                   Option(text="Yesterday", value="now(\"-2d\")"),
                                   Option(text="This week", value="now(\"-1w\")")]

    # приватные диалоги с ботом
    @listen_to(".*", re.IGNORECASE, direct_only=True)
    async def private_dialog_keyboard(self, message: Message):
        keyboard = Keyboard(channel_id=message.channel_id, message="Доступные опции:",
                                   buttons=[Button(name="Настройки",
                                                  url=f"{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}/hooks/settings",
                                                  text="open_settings_modal"),
                                            Button(name="Резюме",
                                                   url=f"{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}/hooks/summary",
                                                   text="open_summary_modal")
                                            ])
        self.driver.posts.create_post(options=keyboard.asdict())

    # обращения к боту в общем чате
    @listen_to(".*", re.IGNORECASE, needs_mention=True)
    async def public_dialog_keyboard(self, message: Message):
        keyboard = Keyboard(channel_id=message.channel_id, message="Доступные опции:",
                            buttons=[Button(name="Резюме",
                                        url=f"{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}/hooks/summary",
                                        text="open_summary_modal")
                                     ])
        self.driver.posts.create_post(options=keyboard.asdict())

    @listen_webhook("settings")
    async def settings_action_dialog(self, event: WebHookEvent):
        print("Context:", event.body.get("context"))
        chats = await session.get_chats_by_nickname(message.from_user.username)
        dialog = Dialog(trigger_id=event.body.get("trigger_id"),
                        url=f"{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}"
                            f"/hooks/settings_result",
                        title='Настройка автоматической генерации резюме',
                        elements=[
                            Element(display_name='', type='select',
                                    options=[Option(text=chat_name, value=chat_id)
                                             for chat_name, chat_id in chats.items()]),
                            Element(display_name='Какое резюме ты хочешь получить?', type='radio',
                                    options=[
                                        Option(text="Today", value="now(\"-1d\")"),
                                        Option(text="Yesterday", value="now(\"-2d\")"),
                                        Option(text="This week", value="now(\"-1w\")")]),
                            Element(display_name='', type='bool', placeholder="Enter date",
                                    optional=True, default="False"
                                    ),
                            Element(display_name='', type='text', placeholder="00:00")
                        ])
        requests.post(f"https://{self.settings.MATTERMOST_URL}:"
                      f"{self.settings.MATTERMOST_PORT}/"
                      f"{self.settings.MATTERMOST_API_PATH}/actions/dialogs/open",
                      json=dialog.asdict())

        print('settings')


    @listen_webhook("settings_result")
    async def settings_result_listener(self, event: WebHookEvent):
        data = event.body['submission']

        # TODO: запрос к бэкенду
        # print(data)
        # search_query = SearchQuery()
        # msg_body = event.body['callback_id']
        # msg = Message(json.loads(msg_body.replace("'", "\"")))
        # search_result = Search(search_text=search_query.search_text, search_results=self.query(search_query)['results'])
        # self.print_search_result(msg, search_result)


    @listen_webhook("summary")
    async def summary_action_dialog(self, event: WebHookEvent):
        chats = await session.get_chats_by_nickname(event.body.get("context")['sender_name'])
        dialog = Dialog(trigger_id=event.body.get("trigger_id"),
                        url=f"{self.settings.WEBHOOK_HOST_URL}:{self.settings.WEBHOOK_HOST_PORT}"
                            f"/hooks/summary_result",
                        title='Параметры генерации резюме',
                        elements=[
                            Element(display_name='Список доступных тебе чатов', type='select',
                                    options=[Option(text=chat_name, value=chat_id)
                                             for chat_name, chat_id in chats.items()]),
                            Element(display_name='Какое резюме ты хочешь получить?', type='radio',
                                    options=[
                                        Option(text="Today", value="now(\"-1d\")"),
                                        Option(text="Yesterday", value="now(\"-2d\")"),
                                        Option(text="This week", value="now(\"-1w\")")]),
                            Element(display_name='', type='bool', placeholder="Use detail date",
                                    optional=True, default="False"
                                    ),
                            Element(display_name='', type='text', placeholder="25.05.2025")
                        ])
        requests.post(f"https://{self.settings.MATTERMOST_URL}:"
                      f"{self.settings.MATTERMOST_PORT}/"
                      f"{self.settings.MATTERMOST_API_PATH}/actions/dialogs/open",
                      json=dialog.asdict())


        print('summary')

    @listen_webhook("summary_result")
    async def summary_result_listener(self, event: WebHookEvent):
        data = event.body['submission']

        # TODO: запрос к бэкенду

        message_body = event.body['callback_id']
        message = Message(json.loads(message_body.replace("'", "\"")))
        message_json = {
            'attachments': [{'text': summary}]
        }
        self.driver.reply_to(message,'', props=message_json)

