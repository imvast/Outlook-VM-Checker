from tls_client import Session
import re
from terminut import log
from concurrent.futures import ThreadPoolExecutor


class LiveLogin:
    def __init__(self):
        self.base_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Host": "login.live.com",
            "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Brave";v="126"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        }
        self.session = Session(client_identifier="chrome_120", random_tls_extension_order=True)
        self.get_cookies()

    def get_cookies(self):
        response = self.session.get("https://login.live.com/", headers=self.base_headers)
        match = re.search(r'name="PPFT".*?value="([^"]*)"', response.text)
        if match:
            ppft_value = match.group(1)
            self._flowToken = ppft_value

        self._uaid = response.text.split("uaid=")[1].split('"')[0]

        return response.cookies

    def check(self, email):
        headers = {
            **self.base_headers,
            "Accept": "application/json",
            "Content-type": "application/json; charset=utf-8",
        }
        payload = {
            "checkPhones": True,
            "country": "",
            "federationFlags": 3,
            "flowToken": self._flowToken,
            "forceotclogin": False,
            "isCookieBannerShown": False,
            "isExternalFederationDisallowed": False,
            "isFederationDisabled": False,
            "isFidoSupported": True,
            "isOtherIdpSupported": False,
            "isRemoteConnectSupported": False,
            "isRemoteNGCSupported": True,
            "isSignup": False,
            "originalRequest": "",
            "otclogindisallowed": False,
            "uaid": self._uaid,
            "username": email,
        }
        response = self.session.post(
            "https://login.live.com/GetCredentialType.srf",
            json=payload,
            headers=headers,
        )
        return response.json()


def main(email):
    live_login = LiveLogin()
    
    res = live_login.check(email)
    if res.get("IfExistsResult") == 0:
        log.info(f"Valid - {email} - {'has phone' if res.get('HasPhone') == 1 else 'no phone'}")
    else:
        log.error(f"Invalid - {email}")
        
        
if __name__ == "__main__":
    with open("emails.txt", "r") as f:
        emails = f.read().splitlines()
        
    with ThreadPoolExecutor(max_workers=10) as executor:
        for email in emails:
            executor.submit(main, email)