from logging import DEBUG, basicConfig


def setup_logger() -> None:
    basicConfig(
        level=DEBUG,
        format="[%(levelname)s]: %(message)s",
    )
