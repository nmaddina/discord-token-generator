from typing import Union
import json, random, string
class Utility:
    def __init__(self) -> None:
        self.config = self.get_config()
        self.username = self.get_username()
        self.proxy = self.get_proxy()
    def get_username(self) -> str:
        return random.choice(open("usernames.txt").read().splitlines()) + "".join(random.choice(string.digits) for _ in range(3))
    def get_config(self) -> dict:
        return json.load(open("config.json"))
    def get_proxy(self) -> Union[str, None]:
        if self.config["proxyless"]:
            return None
        return f"http://{random.choice(open('proxies.txt').read().splitlines())}"