"""
Custom logging handlers and utilities
"""

import logging

log = logging.getLogger(__name__)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ANSI colour codes
BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GREY = "\033[0;37m"
DARK_GREY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
# Reset back to normal
RESET = "\033[0m"


class ColourLogHandler(logging.StreamHandler):
    def __init__(self, show_timestamps, celery_mode, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.formatters = {
            logging.DEBUG: logging.Formatter(
                get_coloured_logging_format(
                    GREEN, show_timestamps=show_timestamps, celery_mode=celery_mode
                )
            ),
            logging.INFO: logging.Formatter(
                get_coloured_logging_format(
                    LIGHT_GREEN,
                    show_timestamps=show_timestamps,
                    celery_mode=celery_mode,
                )
            ),
            logging.WARNING: logging.Formatter(
                get_coloured_logging_format(
                    YELLOW, show_timestamps=show_timestamps, celery_mode=celery_mode
                )
            ),
            logging.ERROR: logging.Formatter(
                get_coloured_logging_format(
                    LIGHT_RED, show_timestamps=show_timestamps, celery_mode=celery_mode
                )
            ),
            logging.CRITICAL: logging.Formatter(
                get_coloured_logging_format(
                    LIGHT_RED, show_timestamps=show_timestamps, celery_mode=celery_mode
                )
            ),
            "DEFAULT": logging.Formatter(
                get_coloured_logging_format(
                    DARK_GREY, show_timestamps=show_timestamps, celery_mode=celery_mode
                )
            ),
        }

    def format(self, record):
        formatter = self.formatters.get(record.levelno, self.formatters["DEFAULT"])
        return formatter.format(record)


def get_base_logging_format_template(show_timestamps, celery_mode):
    meta_format = "{time}{level}{colon}{name}{colon}{message}"

    time = ""
    if show_timestamps:
        time = "{time_colour}%(asctime)s{reset} "

    level = "{level_colour}%(levelname)s"

    colon = "{colon_colour}:"

    if celery_mode:
        name = "{process_name_colour}%(processName)s"
    else:
        name = "{name_colour}%(name)s"

    message = "{reset}%(message)s"

    format_template = meta_format.format(
        time=time, level=level, colon=colon, name=name, message=message
    )

    return format_template


def get_coloured_logging_format(level_colour, show_timestamps=False, celery_mode=False):
    """
    :return Standardized coloured logging format for a specific level
    """
    logging_format = get_base_logging_format_template(
        show_timestamps=show_timestamps, celery_mode=celery_mode
    )

    return logging_format.format(
        time_colour=CYAN,
        reset=RESET,
        level_colour=level_colour,
        colon_colour=DARK_GREY,
        name_colour=BLUE,
        process_name_colour=PURPLE,
    )


def get_logging_format(show_timestamps=False, celery_mode=False):
    """
    :return Standardized logging format
    """
    logging_format = get_base_logging_format_template(
        show_timestamps=show_timestamps, celery_mode=celery_mode
    )

    return logging_format.format(
        time_colour="",
        reset="",
        level_colour="",
        colon_colour="",
        name_colour="",
        process_name_colour="",
    )


def initialise_logging(level, show_timestamps=False, colour=False):
    # Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    handlers = []
    if colour:
        handlers.append(ColourLogHandler(show_timestamps, False))
    else:
        handlers.append(logging.StreamHandler())

    logging_format = get_logging_format(show_timestamps=show_timestamps)

    logging.basicConfig(
        level=level, format=logging_format, datefmt=DATE_FORMAT, handlers=handlers
    )
    log.info(f"Logging set to {logging.getLevelName(level)}")
