from admin.senders import get_themes_inline_buttons
from admin import commands as adm_commands
from base.messages import WELCOME, WELCOME_USER
from db import filters as filters_db, user as user_db
from tg.senders import send_message, forward_message, answer_message
from utils.keyboards import construct_regular_keyboard, construct_inline_keyboard

from . import keyboards, messages


async def send_user_menu(user_id: int):
    return await send_message(user_id,
        WELCOME_USER.from_user(await user_db.get_user(user_id)),
        reply_markup=keyboards.USER_BASE_KEYBOARD
    )


async def send_user_themes_menu(user_id: int, exclude={}, is_admin=True):
    keyboard = await get_themes_inline_buttons(user_id, exclude, is_admin)
    return await send_message(user_id, messages.THEME_LIST,
        reply_markup=construct_regular_keyboard(
            (keyboards.MENU_CLEAR, keyboards.MENU_BACK),
            *keyboard
        ))


async def send_to_admins(filters, message):
    for theme, admin in await filters_db.get_admins_by_filters(filters):
        msg = await forward_message(admin.id, message.chat.id, message.message_id)
        await answer_message(admin.id, msg.message_id,
            f'На тему: {theme}',
            parse_mode='html',
            reply_markup=construct_inline_keyboard({
                    adm_commands.REPLY.name: f'{adm_commands.REPLY.text}{message.message_id}_{message.chat.id}',
                    adm_commands.CHAT.name: f'{adm_commands.CHAT.text}{message.message_id}_{message.chat.id}',
            }))
