# Captcha Manager
#from hcaptchasolve import Hcaptcha
from twocaptcha import TwoCaptcha
import httpx


class CaptchaManager:
    """Captcha Manager"""

    def __init__(self, apiKey: str, captchaApi: str = "anti-captcha.com", proxy: str = None):
        #self.hcaptcha = Hcaptcha(proxy=proxy, timeout=200)
        self.captchaApi = captchaApi
        self.proxy = proxy
        self.apiKey = apiKey
    def solveCaptcha(self):
        #res = self.hcaptcha.solve()
        #return res
        if self.captchaApi == "anti-captcha.com" or self.captchaApi == "capmonster.cloud":
           solvedCaptcha = None
           captchaKey = self.captchaApi
           taskId = ""
           taskId = httpx.post(f"https://api.{self.captchaApi}/createTask", json={"clientKey": captchaKey, "task": {"type": "HCaptchaTask", "websiteURL": "https://discord.com/",
                               "websiteKey": "4c672d35-0701-42b2-88c3-78380b0db560", "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0", "proxyType":"http", "proxyAddress": self.proxy.split("@")[1].split(":")[0] if "@" in self.proxy else self.proxy.split(":")[0],
            "proxyPort": int(self.proxy.split("@")[1].split(":")[1] if "@" in self.proxy else self.proxy.split(":")[1]),
            "proxyLogin":self.proxy.split("@")[0].split(":")[0] if "@" in self.proxy else "None",
            "proxyPassword":self.proxy.split("@")[0].split(":")[1] if "@" in self.proxy else "None",
            "userAgent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
            }}, timeout=30).json()
           if taskId.get("errorId") > 0:
                print(f"[-] createTask - {taskId.get('errorDescription')}!")

           taskId = taskId.get("taskId")
            
           while not solvedCaptcha:
                    captchaData = httpx.post(f"https://api.{self.captchaApi}/getTaskResult", json={"clientKey": captchaKey, "taskId": taskId}, timeout=30).json()
                    if captchaData.get("status") == "ready":
                        solvedCaptcha = captchaData.get("solution").get("gRecaptchaResponse")
                        return solvedCaptcha
        else:
            solver = TwoCaptcha(self.apiKey)
            res = solver.hcaptcha(sitekey="4c672d35-0701-42b2-88c3-78380b0db560", url="discord.com", proxy={"type": "HTTPS", "uri": self.proxy})["code"]
            return res