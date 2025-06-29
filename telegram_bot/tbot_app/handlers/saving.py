from aiogram import Router, types, F

from tbot_app.app import connection
from tbot_app.filters.chat_type import ChatTypeFilter

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)


@router.message(F.content_type.in_({'text'}))
async def message_save(message: types.Message):
    forward_from_username = message.forward_from.username if message.forward_from is not None else None
    reply_id = message.reply_to_message.message_id if message.reply_to_message is not None else None
    data = {'text': message.text, 'timestamp': message.date,
            'source_message_id': message.message_id,
            'reply_source_message_id': reply_id,
            'forward_from': forward_from_username,
            'employee_account': {
                'nickname': message.from_user.username,
                'source': 'Telegram'},
            'chat': {
                'source_chat_id': message.chat.id,
                'chat_source': 'Telegram',
                'name': message.chat.title,
            }}
    await connection.send_message(message=data, queue_name="updates_queue")
    