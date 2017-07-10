from colorama import Fore


def dbprint(typestring, string):
    string = string
    if typestring == 'info':
        print(Fore.LIGHTRED_EX + '[DEBUG]' + Fore.LIGHTYELLOW_EX + '[INFO]' + Fore.WHITE + string)
    elif typestring == 'warning':
        print(Fore.LIGHTRED_EX + '[DEBUG]' + Fore.RED + '[WARNING]' + Fore.WHITE + string)
    elif typestring == 'success':
        print(Fore.LIGHTRED_EX + '[DEBUG]' + Fore.GREEN + '[SUCCESS]' + Fore.WHITE + string)
