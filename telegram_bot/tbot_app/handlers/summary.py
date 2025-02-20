from datetime import datetime, timedelta
from lxml import etree, html
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData

from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback, get_user_locale

from tbot_app.filters.chat_type import ChatTypeFilter
from tbot_app.keyboards.inline_keyboard import make_inline_keyboard
from tbot_app.app import session

router = Router()
router.message.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)
router.callback_query.filter(
    ChatTypeFilter(chat_type=["group", "supergroup"])
)


@router.message(Command("summary"))
async def summary_handler(message: types.Message):
    await message.reply(text="Какое резюме ты хочешь получить?",
        reply_markup=make_inline_keyboard({
            'today_summary': 'Today',
            'yesterday_summary': 'Yesterday',
            'this_week_summary': 'This\n week',
            'calendar_summary': 'Pick a date',
        }))

async def summary_request(session_, source_chat_id, first_date, last_date):
    response = await session_.post_summary(data={"source_chat_id": source_chat_id,
                                        "first_date": first_date, "last_date": last_date})
    if 'text' in response.keys():
        return response['text']
    else:
        return f"No messages for dates from {first_date} to {last_date}"

def html_validation(html_string):
    try:
        parser = html.HTMLParser()
        etree.fromstring(html_string, parser)
        return True
    except etree.XMLSyntaxError:
        return False

@router.callback_query(F.data == "today_summary")
async def summary_for_today_handler(callback: types.CallbackQuery):
    date_ = datetime.today().replace(hour=0, minute=0, second=0)
    summary = await summary_request(session, callback.message.chat.id, date_, date_ + timedelta(days=1))
    if html_validation(summary):
        await callback.message.reply(summary, parse_mode=ParseMode.HTML)
    else:
        await callback.message.reply(summary)
    await callback.answer()

@router.callback_query(F.data == "yesterday_summary")
async def summary_for_yesterday_handler(callback: types.CallbackQuery):
    date_ = datetime.today().replace(hour=0, minute=0, second=0)
    summary = await summary_request(session, callback.message.chat.id,
                                    first_date=date_ - timedelta(days=1), last_date=date_ + timedelta(days=1))
    if html_validation(summary):
        await callback.message.reply(summary, parse_mode=ParseMode.HTML)
    else:
        await callback.message.reply(summary)
    await callback.answer()

@router.callback_query(F.data == "this_week_summary")
async def summary_for_week_handler(callback: types.CallbackQuery):
    date_ = datetime.today().replace(hour=0, minute=0, second=0)
    summary = await summary_request(session, callback.message.chat.id,
                                    first_date=date_ - timedelta(days=7), last_date=date_ + timedelta(days=1))
    if html_validation(summary):
        await callback.message.reply(summary, parse_mode=ParseMode.HTML)
    else:
        await callback.message.reply(summary)
    await callback.answer()


@router.callback_query(F.data == "calendar_summary")
async def calendar_handler(callback: types.CallbackQuery):

    await callback.message.answer(
        "Pick a date: ",
        reply_markup=await SimpleCalendar(
            locale=await get_user_locale(callback.from_user)).start_calendar()
    )
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: CallbackData):
    calendar = SimpleCalendar(
        locale=await get_user_locale(callback.from_user), show_alerts=True
    )
    calendar.set_dates_range(datetime(2022, 1, 1), datetime(2025, 12, 31))
    selected, date_ = await calendar.process_selection(callback, callback_data)
    if selected:
        await callback.message.edit_text("Wait for your summary")
        summary = await summary_request(session, callback.message.chat.id, date_, date_ + timedelta(days=1))
        if html_validation(summary):
            await callback.message.answer(summary, parse_mode=ParseMode.HTML)
        else:
            await callback.message.answer(f"Вот твое резюме:\n{summary}")