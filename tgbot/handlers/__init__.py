from aiogram import Router
from . import admin, user, common

router = Router()


router.include_router(admin.router)
router.include_router(user.router)
router.include_router(common.router)