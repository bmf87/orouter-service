import logging, sys 
from typing import Optional

_LOGGER_NAME = "orouter"
DEBUG = logging.DEBUG


def _create_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        # Already configured (avoid duplicate handlers on reload)
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s - [%(levelname)-4s] - [%(name)s] - ln:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False  # don't double-log via root

    return logger

# Module-level shared logger
logger: logging.Logger = _create_logger()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a child logger with hierarchical name, e.g. 'orouter.ors.llm.llm_loader'.
    """
    if name is None:
        return logger
    return logger.getChild(name)


def set_log_level(level: int | str) -> None:
    """
    Dynamically change log level at runtime.
    Example: set_log_level(logging.DEBUG) or set_log_level("DEBUG").
    """
    if isinstance(level, str):
        level = level.upper()
        level = logging.getLevelName(level)
        if isinstance(level, str):  # invalid name
            raise ValueError(f"Invalid log level name: {level!r}")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def enable_debug_for(module_name: str) -> None:
    """
    Quickly enable DEBUG logging for a sub-module.
    Example: enable_debug_for("ors.llm").
    """
    child = logging.getLogger(f"{_LOGGER_NAME}.{module_name}")
    child.setLevel(logging.DEBUG)


def exception_with_context(msg: str) -> None:
    """
    Log an exception with stack trace in a single call.
    Use inside an except block.
    """
    logger.exception(msg)