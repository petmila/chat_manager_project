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
from tbot_app.states import PrivateSummary,  PrivateAutoGenerationSettings

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


@router.callback_query(F.data.startswith('chat__'), PrivateSummary.chat_id)
async def chats_handler(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(chat_id=callback.data.split("__")[1])
    print(await get_user_locale(callback.from_user))
    await callback.message.reply(
        "Pick a date: ",
        reply_markup=await SimpleCalendar(locale=await get_user_locale(callback.from_user) + '.UTF-8').start_calendar()
    )
    await state.set_state(PrivateSummary.date)
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter(), PrivateSummary.date)
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

# @router.message(Command("chats"))
# async def chats_handler(message: types.Message):
#     await message.reply(text="Какое резюме ты хочешь получить?",
#         reply_markup=make_inline_keyboard({
#             'today_summary': 'Today',
#             'yesterday_summary': 'Yesterday',
#             'this_week_summary': 'This week',
#             'calendar_summary': 'Pick a date',
#         }))
    
@router.message(Command("settings"))
async def settings_handler(message: types.Message, state: FSMContext):
    # chats = await session.get_chats_by_nickname(message.from_user.username)
    chats_keyboard = {"freq__24": "Каждые 24 часа", "freq__168": "Каждую неделю", "freq__72": "Каждые 3 дня"}
    # for chat_name, chat_id in chats.items():
    #     chats_keyboard[f"chat__{chat_id}"] = chat_name
    await state.set_state(PrivateAutoGenerationSettings.frequency)
    await message.reply(text="В боте доступна автоматическая генерация резюме. Выберите частоту генерации",
                        reply_markup=make_inline_keyboard(chats_keyboard))

@router.callback_query(F.data.startswith('freq__'))
async def chats_handler(callback: types.CallbackQuery, state: FSMContext):
    hours = callback.data.split("__")[1]
    await state.update_data(frequency=hours)
    await callback.message.reply(
        "Введите время, в которое вы хотите получать резюме"
    )
    await state.set_state(PrivateAutoGenerationSettings.timestamp)
    await callback.answer()

@router.message(PrivateAutoGenerationSettings.timestamp)
async def process_timestamp(message_: types.Message, state: FSMContext):
    # time_ = datetime.strptime(message_.text, '%H:%M').time()
    await state.update_data(timestamp=message_.text)
    chats = await session.get_chats_by_nickname(message_.from_user.username)
    chats_keyboard = {}
    for chat_name, chat_id in chats.items():
        chats_keyboard[f"chat__{chat_id}"] = chat_name
    await message_.reply(text="Выбери чат, из которого хочешь получить резюме",
                        reply_markup=make_inline_keyboard(chats_keyboard))
    await state.set_state(PrivateAutoGenerationSettings.chat_id)

@router.callback_query(F.data.startswith('chat__'), PrivateAutoGenerationSettings.chat_id)
async def chats_handler_for_settings(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(chat_id=callback.data.split("__")[1])
    data = await state.get_data()
    hours, minutes = data['timestamp'].split(":")
    # freq = timedelta(hours=int(data['frequency']))
    # next_run = datetime.today().replace(hour=int(hours), minute=int(minutes), second=0) + freq
    task_schedule_data = {
        'kwargs': {
            'content_chat': data['chat_id'],
            'source_chat_id': callback.message.chat.id,
        },
        'crontab': {
            'minute': minutes,
            'hour': hours,
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*',
        },
        'task': 'celery.perform_summary_on_chat',
        'name': f"Resume for {callback.message.chat.id} about {data['chat_id']}",
    }
    response = await session.post_task_schedule(task_schedule_data)
    await callback.message.reply(str(task_schedule_data))
    await state.clear()
    await callback.answer()