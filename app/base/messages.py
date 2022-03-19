from utils.messages import UserTemplate


LEAVE_RESPONSE = 'Ваш аккаунт успешно удален'

user_format = '<a href="tg://user?id=$user_id">$first_name $last_name</a>'
user_full_name_format = '$first_name $last_name'
user_short_name_format = '$first_name'

USER = UserTemplate(user_format)
USER_FULL = UserTemplate(user_full_name_format)
USER_SHORT = UserTemplate(user_short_name_format)
WELCOME = UserTemplate(f'Добро пожаловать, {user_short_name_format}!')
WELCOME_USER = UserTemplate('Сообщения, отправленные вами в этом чате будут отправлены администратору по темам, соответствующим вашим настройкам')

YOUR_SETTINGS = 'Ваши настройки'
EMPTY_SETTINGS = 'Ваши настройки пусты'
FITERS_THEMES = 'Tемы'
SET_FILTERS_HERE = 'Вы можете указать настройки отправляемых(принимаемых) сообщений ниже:'
FILTERS_CLEARED = 'Фильтры успешно очищены'
EDIT_YOUR_SETTINGS = 'Вы можете очистить ваши настройки или убрать ненужные вам темы'

CANCEL_BUTTON = 'Отмена'
DELETE_BUTTON = 'Удалить'
CLOSE_CHAT_BUTTON = 'Закрыть чат'

THEME_BUTTON_MODIFIER = '✔️'
