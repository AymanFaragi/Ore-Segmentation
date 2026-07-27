import functools
import logging
import os
import time
from typing import Callable, Optional

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors for log levels
LOG_LEVEL_COLORS = {
    logging.DEBUG: Fore.CYAN,
    logging.INFO: Fore.BLUE,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA,
}


# Create a custom logging formatter to include colors
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = LOG_LEVEL_COLORS.get(record.levelno, Style.RESET_ALL)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


# Configure logging with custom formatter
formatter = ColoredFormatter(
    fmt="%(asctime)s [%(levelname)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.getLogger().addHandler(console_handler)
logging.getLogger().setLevel(logging.DEBUG)


def function_logger(
    start_message: Optional[str] = None,
    end_message: Optional[str] = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            module_name = func.__module__
            if module_name == "__main__":
                file_path = func.__globals__.get("__file__")
                if file_path:
                    module_name = os.path.basename(file_path).replace(".py", "")

            logger = logging.getLogger(module_name)

            if start_message:
                logger.info(
                    f"{Fore.CYAN}{module_name}.{func.__name__}(){Style.RESET_ALL} : "
                    f"{Fore.GREEN}{start_message}{Style.RESET_ALL}"
                )

            try:
                result = func(*args, **kwargs)

                if end_message:
                    end_msg = f"{Fore.GREEN}{end_message}{Style.RESET_ALL}"
                    logger.info(
                        f"{Fore.CYAN}{module_name}.{func.__name__}(){Style.RESET_ALL} : {end_msg}"
                    )
                return result
            except Exception as e:
                logger.exception(
                    f"{Fore.RED}Error in {module_name}.{func.__name__}(){Style.RESET_ALL} : {str(e)}"
                )
                raise

        return wrapper

    return decorator
