from aiogram import types
from aiogram.types.chat import ChatType
from aiogram.dispatcher import FSMContext

from user import keyboards as user_keyboards
from db import filters as filters_db
from config.dependencies import dp
from tg.senders import edit_message
from utils.messages import removeprefix

from . import keyboards, messages, senders


@dp.message_handler(text=keyboards.FILTERS_EDIT_BUTTON, chat_type=ChatType.PRIVATE, state='*')
@dp.message_handler(text=user_keyboards.CURRENT_THEME, chat_type=ChatType.PRIVATE, state='*')
async def edit_filters_themes_list_menu_button(message: types.Message):
    ''' Вывод списка выбранных тем для редактирования '''
    await senders.send_user_editable_menu(message.from_user.id)


@dp.callback_query_handler(text='clear_filters', chat_type=ChatType.PRIVATE, state='*')
async def clear_filters_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Сброс фильтров при нажатии на кнопку под сообщением '''
    await _clear_filters(query.from_user.id, state)
    await edit_message(query.from_user.id, query.message.message_id, messages.FILTERS_CLEARED)


@dp.callback_query_handler(text_startswith=['remove_from_filter_'], chat_type=ChatType.PRIVATE, state='*')
async def remove_theme_from_filter_inline_button(query: types.CallbackQuery, state: FSMContext):
    ''' Сброс фильтров при нажатии на кнопку под сообщением '''
    theme_id = int(removeprefix(query.data, 'remove_from_filter_'))

    filters = await filters_db.get_filters(query.from_user.id)
    await filters_db.remove_theme(filters, theme_id)

    async with state.proxy() as data:
        data['selected_themes'].remove(theme_id)

    text, keyboard = await senders._editable_message(query.message.chat.id)
    await edit_message(
        query.message.chat.id, query.message.message_id,
        text, reply_markup=keyboard
    )


async def _clear_filters(user_id, state):
    filters = await filters_db.get_filters(user_id)
    async with state.proxy() as data:
        await filters.themes.clear()
        data['selected_themes'] = []
