from aiogram import types, Router
from aiogram.filters import Command, CommandObject
from tbot_app.data import post_summary
from tbot_app.app import session

router = Router()

@router.message(Command("chat_summary"))
async def make_summary_command(message: types.Message):
    data = await post_summary(session=session, data={"source_chat_id": message.chat.id})
    await message.reply(f'{data}')
#
# @router.message(Command("chat_summary"))
# async def make_summary_command(message: types.Message, command: CommandObject):
#
#     await message.reply(f'{command.args} вот что было передано в аргументах')


