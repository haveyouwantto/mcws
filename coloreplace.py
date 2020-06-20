from colorama import Fore, init

stylemap = [
    ['0', Fore.BLACK],
    ['1', Fore.BLUE],
    ['2', Fore.GREEN],
    ['3', Fore.LIGHTCYAN_EX],
    ['4', Fore.RED],
    ['5', Fore.MAGENTA],
    ['6', Fore.YELLOW],
    ['7', Fore.LIGHTWHITE_EX],
    ['8', Fore.LIGHTBLACK_EX],
    ['9', Fore.LIGHTCYAN_EX],
    ['a', Fore.LIGHTGREEN_EX],
    ['b', Fore.CYAN],
    ['c', Fore.LIGHTRED_EX],
    ['d', Fore.LIGHTMAGENTA_EX],
    ['e', Fore.LIGHTYELLOW_EX],
    ['f', Fore.WHITE],
    ['k', '\033[5m'],
    ['l', '\033[1m'],
    ['m', '\033[9m'],
    ['n', '\033[4m'],
    ['o', '\033[3m'],
    ['r', '\033[0m']
]

init(autoreset=True)


def replace(text):
    for i in stylemap:
        text = text.replace('§' + i[0], i[1])
    return text + '\033[m'
