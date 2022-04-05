# This is a proof of concept.
# I have seen many people make a discord account generator with browser which is really slow and shit.
# So I made this
from ast import List
from typing import Union
from json import dumps
from traceback import format_exc
from base64 import b64encode as encoder
import httpx
from colorama import Fore, Style
from .emailManager import EmailManager
from .captchaManager import CaptchaManager
from .exceptions import RateLimitException, PatchReqFailException, TokenLockException, EmailNoneException
from .utility import Utility

class Generator:
    """Discord Account Generator Class"""

    def __init__(self, log_token_before_verify: Union[bool, None] = None):
        self.util = Utility()
        self.log_token = log_token_before_verify
        self.client = httpx.Client(cookies={"locale": "en-US"}, headers={
            "Accept": "*/*",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Accept-Language": "en-us",
            "Host": "discord.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            "Referer": "https://discord.com",
            "Accept-Encoding": "br, gzip, deflate",
            "Connection": "keep-alive"
        }, timeout=30, proxies=self.util.proxy)
        self.Captcha = CaptchaManager(proxy=self.util.proxy, apiKey=self.util.config["captcha_key"], captchaApi=self.util.config["captcha_api"])
        self.Email = EmailManager(self.util.config["emailKey"])
        # Get cookies:
        self.client.get("https://discord.com/", headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Host": "discord.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            "Accept-Language": "en-us",
            "Accept-Encoding": "br, gzip, deflate",
            "Connection": "keep-alive"
        })
        del self.client.headers["Accept-Encoding"]
        self.client.headers["X-Track"] = self._build_trackers(
            trackerType="x-track")
        self.fingerprint = self.client.get(
            "https://discord.com/api/v9/experiments").json()["fingerprint"]
        self.client.headers["X-Fingerprint"] = self.fingerprint
        self.client.headers["Origin"] = "https://discord.com"

    def _make_account(self, payload: dict, captcha: Union[str, None] = None) -> dict:
        """Makes a discord account"""
        if captcha != None:
            payload["captcha_key"] = captcha
        return self.client.post("https://discord.com/api/v9/auth/register", json=payload).json()
    def _lock_reason(self) -> str:
        """Gets the reason for token locking"""
        firstIP = self.client.get("https://httpbin.org/ip").json()["origin"]
        secondIP = httpx.get("https://httpbin.org/ip", proxies=self.util.proxy).json()["origin"]
        if firstIP != secondIP:
            return "Proxy is not sticky"
        else:
            return "Proxy is probably flagged."
    def _build_trackers(self, trackerType: str) -> str:
        """Builds the x-track/x-super-properties header"""
        if trackerType == "x-track":
            return encoder(dumps({"os": "Mac OS X", "browser": "Safari", "device": "", "system_locale": "en-us", "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15", "browser_version": "13.1.2", "os_version": "10.13.6", "referrer": "", "referring_domain": "", "referrer_current": "", "referring_domain_current": "", "release_channel": "stable", "client_build_number": 9999, "client_event_source": None}, separators=(',', ':')).encode()).decode()
        elif trackerType == "x-super-properties":
            return encoder(dumps({"os": "Mac OS X", "browser": "Safari", "device": "", "system_locale": "en-us", "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15", "browser_version": "13.1.2", "os_version": "10.13.6", "referrer": "", "referring_domain": "", "referrer_current": "", "referring_domain_current": "", "release_channel": "stable", "client_build_number": 117918, "client_event_source": None}, separators=(',', ':')).encode()).decode()
        else:
            raise Exception("Invalid tracker type. Currently support types('x-track', 'x-super-properties')")
    def generateToken(self) -> tuple[Union[str, None], Union[str, None]]:
        global res
        try:
            payload = {
                "username": self.util.username,
                "fingerprint": self.fingerprint,
                "consent": True,
            }
            self.client.headers["Accept-Encoding"] = "br, gzip, deflate"
            res = self._make_account(payload=payload)
            if 'captcha_key' in res:
                res = self._make_account(
                    payload=payload, captcha=self.Captcha.solveCaptcha())
            elif 'retry_after' in res:
                raise RateLimitException(
                    f"Your proxy: {self.util.proxy}, is ratelimited on discord's api retry after {res['retry_after']}s")
            if self.log_token:
                print(
                    f"{Fore.GREEN}{Style.BRIGHT}Generated unverified token: {res['token']}{Style.RESET_ALL}")
            del self.client.headers["X-Track"]
            del self.client.headers["Accept-Encoding"]
            self.client.headers["Authorization"] = res["token"]
            self.client.headers["X-Debug-Options"] = "bugReporterEnabled"
            self.client.headers["X-Discord-Locale"] = "en-US"
            self.client.headers["Referer"] = "https://discord.com/channels/@me"
            self.client.headers["X-Super-Properties"] = self._build_trackers(
                trackerType="x-super-properties")
            self._send_patch_req()
            res = self._mail_verify()
            if "token" in res:
                self.client.close()
                return res["token"], f"{self.Email.email}:{self.util.config['password']}:{res['token']}"
            else:
                raise TokenLockException(f"{self.client.headers['Authorization']} is locked, Reason: {self._lock_reason()}")
        except (RateLimitException, PatchReqFailException, TokenLockException, EmailNoneException, Exception) as e:
            if self.util.config["log_exceptions"]:
                print(
                    f"[{Fore.RED}{Style.BRIGHT}?{Style.RESET_ALL}] {Fore.YELLOW}{Style.BRIGHT}Exception: {e}{Style.RESET_ALL}")
                if self.util.config["traceback"]:
                    print(format_exc())
            self.client.close()
            return None, None

    def _send_patch_req(self):
        res = self.client.patch("https://discord.com/api/v9/users/@me", json={
            "email": self.Email.get_email(),
            "password": self.util.config["password"],
            "date_of_birth": "1992-01-01"
        }).json()
        if "token" not in res:
            if self.util.config["save_unverified"]:
                req = self.client.get(
                    "https://discord.com/api/v9/users/@me/affinities/guilds")
                if req.status_code != 400 and req.status_code < 400:
                    open("tokens_unverified.txt", "a").write(
                        self.client.headers["Authorization"] + "\n")
            raise PatchReqFailException(
                f"Patch request failed {self.client.headers['Authorization']}")
        self.client.headers["Authorization"] = res["token"]
        self.client.headers["Referer"] = "https://discord.com/verify"

    def _mail_verify(self) -> dict:
        emailData = self.Email.get_discord_token()
        if emailData == False:
            req = self.client.get(
                "https://discord.com/api/v9/users/@me/affinities/guilds")
            if req.status_code != 400 and req.status_code < 400 and self.util.config["save_unverified"]:
                open("tokens_unverified.txt", "a").write(
                    self.client.headers["Authorization"] + "\n")
            raise EmailNoneException(
                f"Kopechka.store did not return a valid EMAIL_TOKEN to email verify")
        res = self.client.post("https://discord.com/api/v9/auth/verify",
                               json={"token": emailData, "captcha_key": None}, timeout=30).json()
        if "token" not in res:
            res = self.client.post("https://discord.com/api/v9/auth/verify",
                                   json={"token": emailData, "captcha_key": None}, timeout=30).json()
        return res
