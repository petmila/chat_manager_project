from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from magic_filter import F

from tbot_app.app import session
from tbot_app.data import post_message

router = Router()

@router.message(F.content_type.in_({'text'}))
async def message_save(message: types.Message):
    reply_id = message.reply_to_message.message_id if message.reply_to_message is not None else None
    data = {'text': message.text, 'timestamp': message.date,
            'source_message_id': message.message_id,
            'reply_source_message_id': reply_id ,
                        'employee_account': {
                            'nickname': message.from_user.username,
                            'source': 'Telegram'},
                        'chat': {
                            'source_chat_id': message.chat.id,
                            'chat_source': 'Telegram',
                            'name': message.chat.title,
                        }}
    await post_message(session, data)


# @router.message(F.content_type.in_({'file'}))
# async def history_save(message: types.Message):
#     data = {'text': message.text, 'timestamp': message.date,
#             "user": {"username": message.from_user.username,
#                      "first_name": message.from_user.first_name,
#                      "last_name": message.from_user.last_name},
#             "source": 'Telegram',
#             "source_chat_id": message.chat.id}
#     input_ = await post_message(data)
#     await message.reply(f'{input_} вот что я сохранил в бд {message.from_user.username}')