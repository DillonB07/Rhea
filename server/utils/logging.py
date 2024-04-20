from typing import Callable

from colorama import Fore, Style

from .messages import info, warn, error

print_info: Callable[[str], None] = lambda message: info(
    f"{Fore.BLUE}Rhea{Style.RESET_ALL} ", message
)
print_warn: Callable[[str], None] = lambda message: warn(
    f"{Fore.BLUE}Rhea{Style.RESET_ALL} ", message
)
print_error: Callable[[str], None] = lambda message: error(
    f"{Fore.BLUE}Rhea{Style.RESET_ALL} ", message
)