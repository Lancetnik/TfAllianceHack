from uuid import UUID

from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from admin import senders as adm_senders
from config.dependencies import dp
from db import user as user_db, themes as theme_db, filters as filters_db
from tg.senders import send_message
from utils.messages import removeprefix

from superuser import commands as s_commands
from admin import commands as adm_commands, states as adm_states
from user import states as usr_states

from . import senders, commands, messages


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=['start'], state='*')
async def process_start_command(message: types.Message, state: FSMContext):
    user = await user_db.get_or_create_user(message.from_user)
    theme_uuid = removeprefix(message.text, '/start').strip()

    async with state.proxy() as data:
        data['prev_state'] = []

        if theme_uuid:
            try:
                theme = await theme_db.get_theme_by_uuid(UUID(theme_uuid))
                await filters_db.add_theme(user, theme.id)

                selected_themes = set(data.get('selected_themes', []) + [theme.id])
                data['selected_themes'] = list(selected_themes)

                await senders.send_user_filters(user.id)
                await adm_senders.send_theme_description(user.id, theme, keyboard=None)
            except Exception:
                pass

    if user.is_admin:
        await adm_states.AdminState.base.set()

    if (user.is_admin or user.is_owner) is False:
        await senders.send_welcome(user)
        await usr_states.UserState.base.set()


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=['help'], state='*')
async def process_help_command(message: types.Message, state: FSMContext):
    user = await user_db.get_or_create_user(message.from_user)

    text = f'Общие команды:\
        \n{commands.LEAVE_COMMAND.help_text}'

    if user.is_admin:
        text = f'Команды администратора:\
        \n{adm_commands.ADMIN_REQUEST_COMMAND.help_text}\
        \n{adm_commands.CREATE_THEME_COMMAND.help_text}\
        \n{adm_commands.THEME_LIST_COMMAND.help_text}\
        \n{adm_commands.DELETE_THEME_COMMAND.help_text}\
        \n{adm_commands.SET_FILTERS_COMMAND.help_text}\
        \n\n{text}'

    if user.is_owner:
        text = f'Команды владельца:\
        \n{s_commands.START_SUPERUSER_COMMAND.help_text}\
        \n{s_commands.CHECK_SUPERUSERS_COMMAND.help_text}\
        \n{s_commands.CHECK_ADMINS_COMMAND.help_text}\
        \n{s_commands.KICK_ADMIN_COMMAND.help_text}\
        \n\n{text}'

    await send_message(message.chat.id, text)


@dp.message_handler(chat_type=ChatType.PRIVATE, commands=[commands.LEAVE_COMMAND.text], state='*')
async def leave_command(message: types.Message):
    user = await user_db.get_or_create_user(message.from_user)
    await user_db.delete_user(user)
    await send_message(message.chat.id,
        messages.LEAVE_RESPONSE, reply_markup=types.ReplyKeyboardRemove()
    )
