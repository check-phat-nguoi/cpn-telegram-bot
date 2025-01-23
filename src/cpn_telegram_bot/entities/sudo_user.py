from beanie import Document


class SudoUser(Document):
    user_ids: tuple[int, ...]
