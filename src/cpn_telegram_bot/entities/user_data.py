from typing import Annotated

from beanie import Document, Indexed
from cpn_core.models.plate_info import PlateInfo
from pymongo import TEXT, IndexModel


class UserData(Document):
    user_id: int
    chat_id: int
    plate_info: Annotated[PlateInfo, Indexed()]
    show_less_detail: bool | None = None

    class Settings:
        indexes: list[IndexModel] = [
            IndexModel(
                [("user_id", TEXT)],
            ),
        ]
        name: str = "user_datas"
