from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from admin import senders as adm_senders
from config.dependencies import dp
from base import senders as base_senders, filters_views as base_view
from db import user as user_db, themes as theme_db, filters as filters_db
from tg.senders import send_message
from utils.messages import removesuffix

from . import keyboards, messages, senders
from .states import UserState


@dp.message_handler(
    text_endswith=[messages.THEME_BUTTON_MODIFIER], chat_type=ChatType.PRIVATE, state=UserState.themes_filters)
async def choose_theme_button(message: types.Message, state: FSMContext):
    ''' Захват нажатия на кнопку выбора темы из меню '''
    theme_name = removesuffix(message.text, messages.THEME_BUTTON_MODIFIER)
    theme = await theme_db.get_theme_by_name(theme_name)

    user = await user_db.get_user(message.from_user.id)
    await filters_db.add_theme(user, theme.id)

    async with state.proxy() as data:
        selected_themes = set(data.get('selected_themes', []) + [theme.id])
        data['selected_themes'] = list(selected_themes)

    await base_senders.send_user_filters(user.id)
    await adm_senders.send_theme_description(user.id, theme, keyboard=None)
    await senders.send_user_themes_menu(user.id, exclude=selected_themes)


@dp.message_handler(text=keyboards.CURRENT_THEME, chat_type=ChatType.PRIVATE, state=UserState.base)
async def show_current_filters_menu_button(message: types.Message):
    ''' Отображение текущих фильтров '''
    await base_senders.send_user_filters(message.from_user.id)


@dp.message_handler(text=keyboards.FILTERS_THEME_BUTTON, chat_type=ChatType.PRIVATE, state=UserState.base)
async def themes_list_menu_button(message: types.Message):
    ''' Вывод списка тем для фильтров по нажатию клавиши в меню '''
    await UserState.themes_filters.set()


@dp.message_handler(text=keyboards.MENU_CLEAR, chat_type=ChatType.PRIVATE, state=UserState.themes_filters)
async def clear_filters_menu_button(message: types.Message, state: FSMContext):
    ''' Сброс фильтров при нажатии на кнопку в меню '''
    await base_view._clear_filters(message.from_user.id, state)
    await send_message(message.chat.id, messages.FILTERS_CLEARED)
    await senders.send_user_themes_menu(message.from_user.id)
