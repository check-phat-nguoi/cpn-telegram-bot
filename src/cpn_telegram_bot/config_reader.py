from os import environ
from sys import stderr
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
        )
    except ValidationError as e:
        print("Failed to read the config!", file=stderr)
        print(e, file=stderr)
        exit(1)


config: Final[ConfigModel] = config_reader()
