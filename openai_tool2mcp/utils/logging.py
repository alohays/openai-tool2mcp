import logging
import sys


def setup_logging(level="info"):
    """
    Set up logging configuration.

    Args:
        level (str): Logging level (debug, info, warning, error, critical)
    """
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    log_level = level_map.get(level.lower(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Create logger for this package
    logger = logging.getLogger("openai_tool2mcp")
    logger.setLevel(log_level)

    return logger


# Create default logger
logger = setup_logging()
