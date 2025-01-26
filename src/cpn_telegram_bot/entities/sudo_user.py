from beanie import Document


class SudoUser(Document):
    user_id: int

    class Settings:
        name: str = "sudo_users"
