from functools import wraps

from telegram import Update, User
from telegram.ext import ContextTypes

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.sudo_user import SudoUser


async def is_sudo(user_id: int) -> bool:
    return user_id in config.OWNERS or user_id in await SudoUser.find_all().to_list()


def sudo_decorator(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user: User | None = update.effective_user
        if user is None:
            return
        user_id: int = user.id
        if not is_sudo(user_id):
            print("Bạn không có quyền sử dụng lệnh này.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
