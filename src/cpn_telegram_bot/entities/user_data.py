from beanie import Document
from cpn_core.models.plate_info import PlateInfo
from pymongo import HASHED, IndexModel


class UserData(Document):
    user_id: PlateInfo
    chat_id: int
    show_less_detail: bool | None = None

    class Settings:
        indexes = [
            IndexModel(
                [("user_id", HASHED)],
            ),
        ]
