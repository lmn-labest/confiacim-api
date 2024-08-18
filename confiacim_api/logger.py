import sys

from loguru import logger

logger.remove()
logger.level("INFO", color="<green>")
logger.add(
    sys.stderr, format="[<b>{time}</b>: <level>{level}</level>] <g>{name}:{module}:{function}:{line}</g> - {message}"
)  # noqa
