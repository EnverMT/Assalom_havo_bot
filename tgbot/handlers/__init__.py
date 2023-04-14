from aiogram import Router
from . import admin, user, common, register

router = Router()


router.include_router(admin.router)
router.include_router(user.router)
router.include_router(common.router)
router.include_router(register.router)