from datetime import datetime, timedelta

from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, get_user_locale, SimpleCalendarCallback

from tbot_app import session
from tbot_app.filters.chat_type import ChatTypeFilter
from tbot_app.handlers.summary import summary_request, html_validation
from tbot_app.keyboards.inline_keyboard import make_inline_keyboard
from tbot_app.states import PrivateSummary

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["private"])
)
router.callback_query.filter(
    ChatTypeFilter(chat_type=["private"])
)

@router.message(Command("summary"))
async def summary_handler(message: types.Message, state: FSMContext):
    chats = await session.get_chats_by_nickname(message.from_user.username)
    chats_keyboard = {}
    for chat_name, chat_id in chats.items():
        chats_keyboard[f"chat__{chat_id}"] = chat_name
    await message.reply(text="Список доступных тебе чатов",
        reply_markup=make_inline_keyboard(chats_keyboard))
    await state.set_state(PrivateSummary.chat_id)


@router.callback_query(F.data.startswith('chat__'))
async def chats_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(chat_id=callback.data.split("__")[1])
    print(await get_user_locale(callback.from_user))
    await callback.message.reply(
        "Pick a date: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(callback.from_user) + '.UTF-8').start_calendar()
    )
    await state.set_state(PrivateSummary.date)
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback.from_user) + '.UTF-8', show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date_ = await calendar.process_selection(callback, callback_data)
    if selected:
        await callback.message.edit_text("Wait for your summary")
        summary = await summary_request(session, data['chat_id'], first_date=date_, last_date=date_ + timedelta(days=1))
        if html_validation(summary):
            await callback.message.answer(summary, parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f"Вот твое резюме:\n{summary}")

@router.message(Command("chats"))
async def chats_handler(message: types.Message):
    await message.reply(text="Какое резюме ты хочешь получить?",
        reply_markup=make_inline_keyboard({
            'today_summary': 'Today',
            'yesterday_summary': 'Yesterday',
            'this_week_summary': 'This week',
            'calendar_summary': 'Pick a date',
        }))