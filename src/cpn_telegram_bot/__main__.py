from asyncio import Event, run
from logging import getLogger

from telegram.ext import ApplicationBuilder, CommandHandler

from cpn_telegram_bot.bot.command_handlers.auth import auth_chat_cov
from cpn_telegram_bot.bot.command_handlers.info import info_handler
from cpn_telegram_bot.bot.command_handlers.start import start_handler
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.modules.setup_logger import setup_logger
from cpn_telegram_bot.services.mongodb import init_db

logger = getLogger(__name__)


async def async_main() -> None:
    setup_logger()
    bot = ApplicationBuilder().token(config.BOT_TOKEN)
    if config.LOCAL_BOT_API_URL is not None:
        bot = bot.base_url(config.LOCAL_BOT_API_URL).local_mode(True)
    async with bot.build() as app:
        await app.start()
        if app.updater is None:
            return
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CommandHandler("info", info_handler))
        app.add_handler(auth_chat_cov)
        await app.updater.start_polling()
        await init_db()
        logger.info("Bot started")
        await Event().wait()
        await app.updater.stop()
        await app.stop()


def main() -> None:
    run(async_main())


if __name__ == "__main__":
    main()
