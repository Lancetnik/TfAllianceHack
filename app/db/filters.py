from typing import List, Tuple

from .models import AdminFilter, User, Theme
from .themes import get_theme


async def get_or_create_filter(user: User) -> AdminFilter:
    return await AdminFilter.objects.get_or_create(user=user)


async def add_theme(user: User, theme_id: int) -> AdminFilter:
    theme = await get_theme(theme_id)
    filters = await get_or_create_filter(user)
    await filters.themes.add(theme)
    return filters


async def get_filters(user_id: int) -> AdminFilter:
    return await AdminFilter.objects\
        .prefetch_related('themes')\
        .filter(user=user_id)\
        .first()


async def remove_theme(filters: AdminFilter, theme_id: int) -> AdminFilter:
    await filters.themes.remove(await get_theme(theme_id))
    return filters


async def get_admins_by_filters(filters: AdminFilter) -> List[Tuple[Theme, User]]:
    return [
        (theme, filter.user)
        for theme in await filters.themes.all()
        for filter in await theme.in_admin_filters.prefetch_related('user').all()
        if filter.user.id != filters.user.id and filter.user.is_admin is True
    ]
