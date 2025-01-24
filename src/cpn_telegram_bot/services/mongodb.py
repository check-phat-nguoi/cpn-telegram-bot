from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from cpn_telegram_bot.config_reader import config
from cpn_telegram_bot.entities.authorized_chat import AuthorizedChat
from cpn_telegram_bot.entities.sudo_user import SudoUser
from cpn_telegram_bot.entities.user_data import UserData


async def init_db() -> None:
    if not config.DB_URI:
        return
    client = AsyncIOMotorClient(config.DB_URI)
    await init_beanie(
        database=client.db_name,
        document_models=[UserData, AuthorizedChat, SudoUser],
    )
