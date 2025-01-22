from typing import Final

from dotenv import dotenv_values

from cpn_tele_bot.models.config import ConfigModel


def config_reader() -> ConfigModel:
    return ConfigModel(**dotenv_values(".env"))  # pyright: ignore[reportArgumentType]


config: Final[ConfigModel] = config_reader()
