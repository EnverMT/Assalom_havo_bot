from aiogram import Router
from . import admin, user


router = Router()


router.include_router(admin.router)
router.include_router(user.router)