from typing import List

from .models import User


async def get_company_owners() -> List[User]:
    return await User.objects.filter(is_owner=True).all()


async def get_company_owners_count() -> int:
    return await User.objects.filter(is_owner=True).count()


async def get_company_admins() -> int:
    return await User.objects.filter(is_admin=True).all()


async def add_company_owner(owner: User) -> None:
    await owner.update(is_owner=True, is_admin=True)


async def add_company_admin(admin: User) -> None:
    await admin.update(is_admin=True)


async def kick_company_admin(admin: User) -> None:
    await admin.update(is_admin=False)


async def kick_company_onwer(owner: User) -> None:
    await owner.update(is_owner=False, is_admin=True)
