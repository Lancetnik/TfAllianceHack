from typing import List, Dict

from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButton, ReplyKeyboardMarkup
)


def construct_inline_keyboard(*args: List[Dict[str, str]]) -> InlineKeyboardMarkup:
    first_row = args[0].items()

    keyboard = InlineKeyboardMarkup(row_width=max(map(len, args)))
    keyboard.row(*(
        InlineKeyboardButton(text, callback_data=data)
        for text, data in first_row
    ))

    for row in args[1:]:
        keyboard.add(*(
            InlineKeyboardButton(text, callback_data=data)
            for text, data in row.items()
        ))
    return keyboard


def construct_regular_keyboard(*args: List[List[str]]) -> ReplyKeyboardMarkup:
    first_row = args[0]

    keyboard = ReplyKeyboardMarkup(row_width=max(map(len, args)))
    keyboard.row(*(
        KeyboardButton(text)
        for text in first_row
    ))

    for row in args[1:]:
        keyboard.add(*(
            KeyboardButton(text)
            for text in row
        ))
    return keyboard


def slice_by_rows(iterable, step=2, func=lambda x: x):
    i = 0
    buf = []
    buttons = []
    for obj in iterable:
        if i == step:
            buttons.append(buf)
            buf = [func(obj)]
            i = 1
        else:
            buf.append(func(obj))
            i += 1
    if buf:
        buttons.append(buf)
    return buttons
