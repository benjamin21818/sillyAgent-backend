import logging
from colorlog import ColoredFormatter, escape_codes

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(log_color)s%(log_color)s%(log_color)s%(levelname)s%(reset)s %(name)s:%(lineno)d: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_COLORS = {
    "DEBUG": "cyan",
    "INFO": "green",
    "WARNING": "yellow",
    "ERROR": "red",
    "CRITICAL": "bold_red",
}

formatter = ColoredFormatter(
    LOG_FORMAT,
    datefmt=DATE_FORMAT,
    log_colors=LOG_COLORS,
)

class BoxedColoredFormatter(ColoredFormatter):
    def format(self, record):
        base = super().format(record)
        lines = base.splitlines() or [""]
        width = max(len(line) for line in lines)
        color_name = self.log_colors.get(record.levelname, "")
        color_code = escape_codes.escape_codes.get(color_name, "")
        reset = escape_codes.escape_codes.get("reset", "\x1b[0m")
        top = f"{color_code}┌{'─' * (width + 2)}┐{reset}"
        middle = [f"{color_code}│ {line.ljust(width)} │{reset}" for line in lines]
        bottom = f"{color_code}└{'─' * (width + 2)}┘{reset}"
        return "\n".join([top, *middle, bottom])

base_logger = logging.getLogger("sillyagent")
base_logger.setLevel(logging.INFO)
base_logger.propagate = False

def get_logger(name: str):
    return base_logger.getChild(name)

def add_boxed_handler(level: int = logging.INFO):
    for existing in base_logger.handlers:
        if getattr(existing, "_boxed_handler", False):
            return existing
    boxed_handler = logging.StreamHandler()
    boxed_handler.setLevel(level)
    boxed_handler.setFormatter(
        BoxedColoredFormatter(
            LOG_FORMAT,
            datefmt=DATE_FORMAT,
            log_colors=LOG_COLORS,
        )
    )
    boxed_handler._boxed_handler = True
    base_logger.addHandler(boxed_handler)
    return boxed_handler

add_boxed_handler()
