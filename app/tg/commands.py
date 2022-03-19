from typing import Protocol


class classproperty:
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner, cls):
        return self.fget(cls)


class Command(Protocol):
    text: str

    @classproperty
    def help_text(cls):
        raise NotImplementedError('Implement `help_text` property')

    def __str__(self):
        return self.text
