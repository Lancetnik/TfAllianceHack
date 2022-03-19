from base.keyboards import MENU_BACK, FILTERS_THEME_BUTTON, FILTERS_EDIT_BUTTON
from user.keyboards import MENU_CLEAR
from utils.keyboards import construct_inline_keyboard, construct_regular_keyboard

from . import messages


CANCEL_THEME_CREATION_KEYBOARD = construct_inline_keyboard({
    messages.CANCEL_BUTTON: 'cancel_theme_creation'
})


CANCEL_MESSAGING_KEYBOARD = construct_inline_keyboard({
    messages.CANCEL_BUTTON: 'cancel_messaging'
})


CREATE_NEW_THEME_INLINE_BUTTON = {
    messages.CREATE_NEW_THEME: "create_new_theme"
}


MENU_THEME_BUTTON = 'Cписок тем🗂'
MENU_FILTERS_BUTTON = 'Фильтр сообщений🔎'
MESSAGES_MENU = 'Сообщения📪'
MENU_BLACK_LIST_BUTOON = 'Черный список'

ADMIN_BASE_KEYBOARD = construct_regular_keyboard(
    (MENU_THEME_BUTTON, MENU_FILTERS_BUTTON,),
    (MESSAGES_MENU,),
)


NEW_THEME_BUTTON = 'Новая тема✍️'
ADMIN_THEMES_ROW = (NEW_THEME_BUTTON, MENU_BACK)

WATCH_MESSAGES = 'Просмотр📭'
SEND_MESSAGES = 'Отправка📨'
MESSAGES_MENU_KEYBOARD = construct_regular_keyboard(
    (WATCH_MESSAGES, MENU_BACK),
    (SEND_MESSAGES,)
)


SEND_TO_GROUP = 'Группа👥'
SEND_TO_CHANNEL = 'Канал🔈'
SEND_TO_THEME = 'Тема🗂'
SEND_MESSAGE = 'Отправить📨'
SEE_ALL_MESSAGES = 'Все сообщения🗒'
MESSAGES_SEND_KEYBOARD = construct_regular_keyboard(
    (SEND_TO_GROUP, SEND_TO_THEME, SEND_TO_CHANNEL),
    (MENU_BACK, MENU_CLEAR, SEND_MESSAGE),
)
