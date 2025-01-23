from os import environ
from typing import Final

from dotenv import dotenv_values
from pydantic import ValidationError

from cpn_telegram_bot.models.config import ConfigModel


def config_reader() -> ConfigModel:
    try:
        return ConfigModel(
            **{
                **dotenv_values(".env"),
                **environ,
            }
        )  # pyright: ignore[reportArgumentType]
    except ValidationError as e:
        print(f"Config read failed. {e}")
        exit(1)


config: Final[ConfigModel] = config_reader()
