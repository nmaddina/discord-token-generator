# Author: Shahzain, Github: idk rn, i might release it but some people will sell it for hundreds of $. especially indians.
# Took me about 1-2 hours to make.
from generator import Generator, Utility
from traceback import format_exc
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from os import system, name
from pyfiglet import figlet_format


def main(log_token_before_verify: bool = True):
    utils = Utility()
    while True:
        try:
            gen = Generator(log_token_before_verify=log_token_before_verify)
            token, formattedToken = gen.generateToken()
            if token != None:
                print(
                    f"[{Fore.LIGHTBLUE_EX}{Style.BRIGHT}>{Style.RESET_ALL}] {Fore.GREEN}{Style.BRIGHT}Generated token: {token}{Style.RESET_ALL}")
                open("tokens.txt", "a").write(token + "\n")
                open("tokens_format.txt", "a").write(formattedToken + "\n")
        except Exception as e:
            print(
                f"[{Fore.RED}{Style.BRIGHT}?{Style.RESET_ALL}] {Fore.YELLOW}{Style.BRIGHT}Exception: {e}{Style.RESET_ALL}")
            if utils.config["traceback"]:
                print(format_exc())


if __name__ == "__main__":
    system("cls") if name == "nt" else system("clear")
    print(Fore.GREEN + Style.BRIGHT +
          figlet_format("Shahzain Token Generator") + Style.RESET_ALL)
    threadCount = int(
        input(f"[{Fore.LIGHTBLUE_EX}{Style.BRIGHT}>{Style.RESET_ALL}] {Fore.GREEN}{Style.BRIGHT}Enter thread count: {Style.RESET_ALL}")
    )
    with ThreadPoolExecutor(max_workers=threadCount) as ex:
        for x in range(threadCount):
            ex.submit(main)
