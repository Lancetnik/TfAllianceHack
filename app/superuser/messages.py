from base.messages import WELCOME


SUPERUSER_CREATED = WELCOME
ALREADY_HAVE_SUPERUSER = "Ваша заявка отправлена.\nЖдите подтверждения администратора."
ALREADY_SUPERUSER = 'Вы уже являетесь владельцем компании'

ADMIN_REQUEST_NOTIFICATION = 'Пользователь %s хочет стать администратором компании'
OWNER_REQUEST_NOTIFICATION = 'Пользователь %s хочет стать совладельцем компании'
ADMIN_CONFIRMED_NOTIFICATION = 'Заявка пользователя %s на администрирование компании одобрена администратором %s'
ADMIN_CONFIRMED_ANSWER = 'Вы произведены в администраторы компании'
ADMIN_DENY_NOTIFICATION = 'Заявка пользователя %s на администрирование компании отклонена администратором %s'
ADMIN_DENY_ANSWER = 'Ваша заявка на администрирование компании отклонена'
OWNER_CONFIRMED_NOTIFICATION = 'Пользователь %s производится администратором %s в совладельцы компании'
OWNER_CONFIRMED_ANSWER = 'Вы произведены в совладельцы компании'

CONFIRM_BUTTON = 'Принять✅'
DENY_BUTTON = 'Отклонить❌'
MAKE_ADMIN_BUTTON = 'Сделать администратором'
MAKE_OWNER_BUTTON = 'Сделать совладельцем'

ADMIN_LIST = 'Администраторы:\n'
OWNER_LIST = 'Совладельцы:\n'

ADMIN_KICKED = 'Пользователь %s исключен из списка администраторов владельцем %s'
ADMIN_NOT_FOUND = 'Администратор с именем %s не найден'
TRY_KICK_YOURSELF = 'Вы не можете удалить себя из списка администраторов'
YOU_KICKED = 'Вы были исключены из состава администраторов'
