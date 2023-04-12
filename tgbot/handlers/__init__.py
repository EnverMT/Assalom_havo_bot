from aiogram import Router
from . import admin


router = Router()


router.include_router(admin.router)