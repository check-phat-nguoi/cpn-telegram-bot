from asyncio import Event, run

from telegram.ext import ApplicationBuilder, CommandHandler

from cpn_telegram_bot.bot.command_handlers.info import info_handler
from cpn_telegram_bot.bot.command_handlers.start import start_handler
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.services.mongodb import init_db


async def async_main() -> None:
    async with ApplicationBuilder().token(config.BOT_TOKEN).build() as app:
        await app.start()
        if app.updater is None:
            return
        app.add_handler(CommandHandler("start", start_handler))
        app.add_handler(CommandHandler("info", info_handler))
        await app.updater.start_polling()
        await init_db()
        await Event().wait()
        await app.updater.stop()
        await app.stop()


def main() -> None:
    run(async_main())


if __name__ == "__main__":
    main()
