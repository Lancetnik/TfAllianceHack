from utils.keyboards import construct_regular_keyboard


FILTERS_EDIT_BUTTON = 'Текущие настройки⚙️'
FILTERS_THEME_BUTTON = 'Темы🗂'
MENU_BACK = 'Назад◀️'

FILTERS_KEYBOARD = construct_regular_keyboard(
    (FILTERS_THEME_BUTTON, MENU_BACK),
    (FILTERS_EDIT_BUTTON,)
)


CLEAR_BUTTON = 'Очистить'
CLEAR_FILTERS_ROW = {
    CLEAR_BUTTON: 'clear_filters'
}
