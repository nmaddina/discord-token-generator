# Email Manager
# Supports: IMAP, Kopeecka.store
import httpx
from time import sleep
from typing import Union
class EmailManager:
    """
    # Email Manager
    """
    def __init__(self, emailKey: str):
        self.emailKey = emailKey
    def get_email(self) -> Union[str, None]:
        """
        # Gets email from kopechka.store
        """
        res = httpx.get(
        f'https://api.kopeechka.store/mailbox-get-email?api=2.0&spa=1&site=discord.com&sender=discord&regex=&mail_type=REAL&token={self.emailKey}', timeout=30).json()
        if res["status"] == "OK":
            self.emailId = res["id"]
            self.email = res["mail"]
            return res["mail"]
        else: 
            return None
    def get_discord_token(self) -> Union[str, bool]:
        # 30 retries
        for i in range(30):
            sleep(2)
            res = httpx.get(f"https://api.kopeechka.store/mailbox-get-message?full=1&spa=1&id={self.emailId}&token={self.emailKey}", timeout=30).json()
            if res["value"] != "WAIT_LINK":
                httpx.get(f"https://api.kopeechka.store/mailbox-cancel?id={self.emailId}&token={self.emailKey}")
                return httpx.get(res["value"], headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US", "Connection": "keep-alive", "DNT": "1", "Host": "click.discord.com", "Sec-Fetch-Dest": "document",
                               "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"}).headers.get("location").split("=")[1]
            else: 
                continue
        return False