from telegram.ext import ApplicationBuilder, CommandHandler

from cpn_telegram_bot.bot.command_handlers.start import start
from cpn_telegram_bot.config_reader import config


def main() -> None:
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
