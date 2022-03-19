from tg.commands import Command, classproperty


class LEAVE_COMMAND(Command):
    text = 'leave'

    @classproperty
    def help_text(cls):
        return f'/{cls.text} - удалить аккаунт'
