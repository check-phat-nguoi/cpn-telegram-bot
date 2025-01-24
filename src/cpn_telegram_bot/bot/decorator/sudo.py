from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.sudo_user import SudoUser


def sudo(func):
    @wraps(func)
    async def wrapped(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = update.effective_user
        if user is None:
            return
        user_id = user.id
        if (
            user_id not in config.OWNERS
            or user_id not in await SudoUser.find_all().to_list()
        ):
            print("Bạn không có quyền sử dụng lệnh này.")
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
