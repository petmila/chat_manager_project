from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



def make_inline_keyboard(items: dict) -> InlineKeyboardMarkup:
    rows = []
    for key, value in items.items():
        rows.append(
            [InlineKeyboardButton(
                text=value,
                callback_data=key)])

    markup = InlineKeyboardMarkup(inline_keyboard=rows, resize_keyboard=True)
    return markup