from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from tbot_app.data import post_summary
from tbot_app.app import session
from aiogram.enums import ParseMode
router = Router()


@router.message(Command("chat_summary"))
async def make_summary_command(message: types.Message, command: CommandObject):
    print(command.args)
    # data = await post_summary(session=session, data={"source_chat_id": message.chat.id,
    #                                                  'datetime_': command.args})
    try:
        await message.reply(data['text'], parse_mode=ParseMode.HTML)
    except BaseException:
        await message.reply(data['text'])
# @router.message(Command("chat_summary"))
# async def make_summary_command(message: types.Message, command: CommandObject):
#
#     await message.reply(f'{command.args} вот что было передано в аргументах')
