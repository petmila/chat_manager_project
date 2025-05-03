from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from tbot_app.app import session, bot
from tbot_app.chat_history_parsing import parse_chat_history
from tbot_app.filters.chat_type import ChatTypeFilter

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)

@router.message(Command("upload_history"))
async def upload_history_command(message: types.Message):
    try:
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        history = parse_chat_history(downloaded_file.getvalue(),
                                     file_path=file_id + ".json",
                                     source_chat_id=message.chat.id,
                                     chat_title=message.chat.title)
        for message_ in history:
            post = await session.post_message(message_)
    except BaseException as e:
        print(e.args)
        await message.reply(f'Ошибка')

