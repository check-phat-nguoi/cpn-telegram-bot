from logging import INFO, basicConfig


def setup_logger() -> None:
    basicConfig(
        level=INFO,
        format="[%(levelname)s]: %(message)s",
    )
