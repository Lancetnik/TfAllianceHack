from base import keyboards as base_keyboards
from utils.keyboards import construct_regular_keyboard


CURRENT_THEME = 'Текущие настройки⚙️'
MENU_CLEAR = 'Очистить❌'
MENU_BACK = base_keyboards.MENU_BACK
FILTERS_THEME_BUTTON = base_keyboards.FILTERS_THEME_BUTTON

USER_BASE_KEYBOARD = construct_regular_keyboard(
    (FILTERS_THEME_BUTTON, CURRENT_THEME,)
)
