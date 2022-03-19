from string import Template


class UserTemplate(Template):
    def from_user(self, user, **kwargs) -> str:
        return self.substitute(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name or "",
            **kwargs
        )

def removeprefix(text: str, prefix: str, /) -> str:
    if text.startswith(prefix):
        return text[len(prefix):]
    else:
        return text[:]


def removesuffix(text: str, suffix: str, /) -> str:
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    else:
        return text[:]
