from asyncio import run

from telegram.ext import ApplicationBuilder, CommandHandler

from cpn_telegram_bot.bot.command_handlers.start import start
from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.services.mongodb import init_db


async def async_main() -> None:
    await init_db()
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


def main() -> None:
    run(async_main())


if __name__ == "__main__":
    main()
