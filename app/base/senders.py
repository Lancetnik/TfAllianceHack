from aiogram.types import InlineKeyboardMarkup

from db import user as user_db, filters as filters_db
from tg.senders import send_message
from utils.keyboards import construct_inline_keyboard

from . import messages, keyboards


async def send_filters_menu(user_id: int):
    return await send_message(user_id,
        messages.SET_FILTERS_HERE,
        reply_markup=keyboards.FILTERS_KEYBOARD
    )


async def send_welcome(user):
    return await send_message(user.id, messages.WELCOME.from_user(user))


async def send_user_filters(user_id: int):
    return await send_message(
        user_id, _user_filters_message(await _user_themes(user_id))
    )


async def send_filters_cleared(user_id: int):
    return await send_message(user_id, messages.FILTERS_CLEARED)


async def send_user_editable_menu(user_id: int):
    text, keyboard = await _editable_message(user_id)
    return await send_message(user_id, text,
        reply_markup=keyboard
    )


async def _editable_message(user_id: int) -> (str, InlineKeyboardMarkup):
    themes = await _user_themes(user_id)
    if themes:
        return f'{_user_filters_message(themes)}\n\n{messages.EDIT_YOUR_SETTINGS}', \
            construct_inline_keyboard(keyboards.CLEAR_FILTERS_ROW, *(
                {theme.name: f'remove_from_filter_{theme.id}'} for theme in themes
            ))
    else:
        return messages.EMPTY_SETTINGS, None


async def _user_themes(user_id: int):
    user = await user_db.get_user(user_id)
    filters = await user.admin_filters.all()  # not .first()! -> error as empty

    if filters:
        filters = filters[0]
    else:
        filters = await filters_db.get_or_create_filter(user)

    return await filters.themes.all()


def _user_filters_message(themes) -> str:
    if themes:
        return messages.YOUR_SETTINGS + \
            f'\n{messages.FITERS_THEMES}:\n' + \
            '\n'.join(tuple(f'{i+1}) {theme}' for i, theme in enumerate(themes)))
    else:
        return messages.EMPTY_SETTINGS
