"""
WOS-M WhiteoutProject Provider - Real Gift Code Redemption
Based on: https://github.com/whiteout-project/bot

Real redemption path:
1. /api/player - Player lookup
2. /api/captcha - Fetch CAPTCHA
3. OCR solve
4. /api/gift_code - Redeem
"""
import asyncio, hashlib, time, ssl, certifi, aiohttp, base64, random, logging
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum

from config.settings import settings
from integrations.browser_headers import get_headers

logger = logging.getLogger(__name__)

class RedemptionStatus(Enum):
    SUCCESS = "SUCCESS"; RECEIVED = "RECEIVED"; SAME_TYPE_EXCHANGE = "SAME TYPE EXCHANGE"
    TOO_POOR_SPEND_MORE = "TOO_POOR_SPEND_MORE"; TOO_SMALL_SPEND_MORE = "TOO_SMALL_SPEND_MORE"
    TIME_ERROR = "TIME_ERROR"; CDK_NOT_FOUND = "CDK_NOT_FOUND"; USAGE_LIMIT = "USAGE_LIMIT"
    NOT_LOGIN = "NOT_LOGIN"; UNAUTHORIZED = "UNAUTHORIZED"; LOGIN_FAILED = "LOGIN_FAILED"
    CAPTCHA_ERROR = "CAPTCHA_ERROR"; CAPTCHA_INVALID = "CAPTCHA_INVALID"
    CAPTCHA_TOO_FREQUENT = "CAPTCHA_TOO_FREQUENT"; CAPTCHA_FETCH_ERROR = "CAPTCHA_FETCH_ERROR"
    SOLVER_ERROR = "SOLVER_ERROR"; OCR_DISABLED = "OCR_DISABLED"
    SIGN_ERROR = "SIGN_ERROR"; TIMEOUT_RETRY = "TIMEOUT_RETRY"
    CONNECTION_ERROR = "CONNECTION_ERROR"; ERROR = "ERROR"; UNKNOWN_API_RESPONSE = "UNKNOWN_API_RESPONSE"

@dataclass
class PlayerInfo:
    fid: str; name: Optional[str] = None; level: Optional[int] = None
    alliance: Optional[str] = None; alliance_id: Optional[str] = None

@dataclass
class RedeemResult:
    status: RedemptionStatus; message: str
    player_info: Optional[PlayerInfo] = None; raw_response: Optional[Dict] = None

class WhiteoutProjectProvider:
    API_BASE = "https://wos-giftcode-api.centurygame.com"
    API_PLAYER = "https://wos-giftcode-api.centurygame.com/api/player"
    API_CAPTCHA = "https://wos-giftcode-api.centurygame.com/api/captcha"
    API_REDEEM = "https://wos-giftcode-api.centurygame.com/api/gift_code"
    SIGN_SALT = "tB87#kPtkxqOS2"
    RATE_LIMIT = 30; RATE_WINDOW = 60; MAX_RETRIES = 3; RETRY_DELAY = 3.0

    def __init__(self):
        self._session = None; self._ocr = None; self._ocr_ok = False
        self.provider_name = settings.api.external_provider_name or "WhiteoutProject"
        self.api_base = settings.api.external_provider_url or self.API_BASE
        self.api_key = settings.api.external_provider_api_key or ""
        self.login_token = settings.api.external_provider_login_token or ""
        self.cookie = settings.api.external_provider_cookie or ""
        self.session_id = settings.api.external_provider_session or ""
        self.sign_secret = settings.api.external_provider_sign_secret or self.SIGN_SALT
        self._r1 = []; self._r2 = []; self._enabled = False; self._test_result = None
        self._init_ocr()

    def _init_ocr(self):
        try:
            import ddddocr
            self._ocr = ddddocr.DdddOcr(show_ad=False); self._ocr_ok = True
            logger.info("ddddocr initialized")
        except: logger.warning("ddddocr not installed"); self._ocr_ok = False

    def is_configured(self): return bool(self.api_key or self.login_token or self.cookie or self.session_id)
    def is_enabled(self): return self._enabled
    def get_status(self):
        if self._enabled: return f"Enabled ({self.provider_name})"
        elif self.is_configured(): return f"Configured - {self._test_result or 'Unknown'}"
        return "Locked - Missing credentials"

    async def init(self):
        if not self._session:
            ctx = ssl.create_default_context(cafile=certifi.where())
            self._session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ctx), trust_env=True)

    async def close(self):
        if self._session: await self._session.close(); self._session = None

    def _sign(self, params):
        s = "&".join(f"{k}={v}" for k,v in sorted(params.items())) + self.sign_secret
        return hashlib.md5(s.encode()).hexdigest()

    def _hdrs(self, url=""):
        h = get_headers(url) if url else get_headers()
        if self.api_key: h["X-API-Key"] = self.api_key
        if self.login_token: h["X-Login-Token"] = self.login_token
        if self.cookie: h["Cookie"] = self.cookie
        if self.session_id: h["X-Session-ID"] = self.session_id
        return h

    def _check_rate(self, api):
        now = time.time(); lst = self._r1 if api==1 else self._r2
        lst[:] = [t for t in lst if now-t < self.RATE_WINDOW]
        if len(lst) >= self.RATE_LIMIT: return self.RATE_WINDOW - (now-min(lst))
        lst.append(now); return 0

    async def _wait_rate(self, api=1):
        w = self._check_rate(api)
        if w > 0: w += random.uniform(0,.5); await asyncio.sleep(w)

    async def test(self):
        await self.init(); await self._wait_rate(1)
        now = int(time.time()*1000); params = {"fid": "45379845", "time": now}
        sign = self._sign(params)
        try:
            async with self._session.post(self.API_PLAYER, headers=self._hdrs(self.API_BASE),
                data={"fid": "45379845", "time": now, "sign": sign}, timeout=aiohttp.ClientTimeout(total=15)) as r:
                if r.status == 403:
                    self._enabled = False; self._test_result = "Unauthorized"
                    return False, "UNAUTHORIZED - API requires credentials"
                if r.status == 200:
                    res = await r.json()
                    if res.get("msg") == "success":
                        self._enabled = True; self._test_result = "Connected"
                        return True, "SUCCESS - API connected"
                    elif res.get("msg") == "NOT LOGIN":
                        self._enabled = True; self._test_result = "NOT_LOGIN"
                        return True, "NOT_LOGIN - but API responding"
                self._enabled = False; self._test_result = f"Error {r.status}"
                return False, f"API status {r.status}"
        except asyncio.TimeoutError:
            self._enabled = False; self._test_result = "Timeout"
            return False, "Timeout"
        except Exception as e:
            self._enabled = False; self._test_result = str(e)
            return False, f"Error: {e}"

    async def get_player(self, fid):
        await self.init(); await self._wait_rate(1)
        now = int(time.time()*1000); params = {"fid": fid, "time": now}; sign = self._sign(params)
        for _ in range(self.MAX_RETRIES):
            try:
                async with self._session.post(self.API_PLAYER, headers=self._hdrs(self.API_BASE),
                    data={"fid": fid, "time": now, "sign": sign}, timeout=aiohttp.ClientTimeout(total=30)) as r:
                    if r.status == 403: return False, None, "UNAUTHORIZED"
                    try: res = await r.json()
                    except: return False, None, "INVALID_RESPONSE"
                    if res.get("msg") == "success":
                        d = res.get("data", {})
                        return True, PlayerInfo(fid=fid, name=d.get("name"), level=d.get("level"),
                            alliance=d.get("alliance"), alliance_id=d.get("alliance_id")), "success"
                    elif res.get("msg") == "NOT LOGIN": return False, None, "NOT_LOGIN"
                    else: return False, None, res.get("msg", "LOGIN_ERROR")
            except: await asyncio.sleep(self.RETRY_DELAY)
        return False, None, "MAX_RETRIES"

    async def fetch_captcha(self, fid):
        await self.init(); await self._wait_rate(1)
        now = int(time.time()*1000); params = {"fid": fid, "init": 0, "time": now}; sign = self._sign(params)
        try:
            async with self._session.post(self.API_CAPTCHA, headers=self._hdrs(self.API_BASE),
                data={"fid": fid, "time": now, "init": 0, "sign": sign}, timeout=aiohttp.ClientTimeout(total=30)) as r:
                try: js = await r.json()
                except: return False, None, "INVALID_RESPONSE"
                err = js.get("err_code")
                if err == 0:
                    img = js.get("data", {}).get("img", "")
                    if img:
                        b = base64.b64decode(img.split(",",1)[1]) if "," in img else base64.b64decode(img)
                        return True, b, "success"
                    return False, None, "INVALID_IMAGE"
                elif err == 40100: return False, None, "INVALID_FID"
                elif js.get("msg") == "NOT LOGIN": return False, None, "NOT_LOGIN"
                return False, None, f"CAPTCHA_ERROR_{err}"
        except Exception as e: return False, None, f"ERROR: {e}"

    def solve_captcha(self, img):
        if not self._ocr_ok or not self._ocr: return None
        try: r = self._ocr.classification(img); return r if r else None
        except: return None

    async def redeem(self, code, fid):
        await self.init()
        ok, pinfo, err = await self.get_player(fid)
        if not ok:
            if err == "NOT_LOGIN": return RedeemResult(RedemptionStatus.NOT_LOGIN, "API requires login", pinfo)
            if err == "UNAUTHORIZED": return RedeemResult(RedemptionStatus.UNAUTHORIZED, "API requires auth", pinfo)
            return RedeemResult(RedemptionStatus.ERROR, f"Player lookup failed: {err}", pinfo)
        
        ok, cap, err = await self.fetch_captcha(fid)
        if not ok or cap is None:
            if err == "NOT_LOGIN": return RedeemResult(RedemptionStatus.NOT_LOGIN, "CAPTCHA requires login", pinfo)
            return RedeemResult(RedemptionStatus.CAPTCHA_FETCH_ERROR, f"CAPTCHA failed: {err}", pinfo)
        
        if not self._ocr_ok: return RedeemResult(RedemptionStatus.OCR_DISABLED, "OCR not available", pinfo)
        captcha = self.solve_captcha(cap)
        if not captcha: return RedeemResult(RedemptionStatus.SOLVER_ERROR, "OCR failed", pinfo)
        
        await self._wait_rate(1)
        now = int(time.time()*1000); params = {"captcha_code": captcha, "cdk": code, "fid": fid, "time": now}
        sign = self._sign(params)
        
        for _ in range(self.MAX_RETRIES):
            try:
                async with self._session.post(self.API_REDEEM, headers=self._hdrs(self.API_BASE),
                    data={"cdk": code, "fid": fid, "time": now, "captcha_code": captcha, "sign": sign},
                    timeout=aiohttp.ClientTimeout(total=30)) as r:
                    try: res = await r.json()
                    except: return RedeemResult(RedemptionStatus.ERROR, "Invalid response", pinfo)
                    
                    err_code = res.get("err_code"); msg = res.get("msg", "")
                    m = {20000: (RedemptionStatus.SUCCESS, "Claimed"), 40008: (RedemptionStatus.RECEIVED, "Already claimed"),
                        40014: (RedemptionStatus.CDK_NOT_FOUND, "Code not found"), 40007: (RedemptionStatus.TIME_ERROR, "Expired"),
                        40005: (RedemptionStatus.USAGE_LIMIT, "Fully claimed"), 40009: (RedemptionStatus.NOT_LOGIN, "NOT LOGIN"),
                        40103: (RedemptionStatus.CAPTCHA_INVALID, "CAPTCHA invalid")}
                    if err_code in m: s, t = m[err_code]; return RedeemResult(s, t, pinfo, res)
                    if msg == "success": return RedeemResult(RedemptionStatus.SUCCESS, "Claimed", pinfo, res)
                    return RedeemResult(RedemptionStatus.UNKNOWN_API_RESPONSE, f"err={err_code}", pinfo, res)
            except asyncio.TimeoutError: await asyncio.sleep(self.RETRY_DELAY)
            except: await asyncio.sleep(self.RETRY_DELAY)
        return RedeemResult(RedemptionStatus.ERROR, "Max retries", pinfo)

    @property
    def has_ocr(self): return self._ocr_ok
    def info(self): return {"name": self.provider_name, "enabled": self._enabled, "configured": self.is_configured(),
        "ocr": self._ocr_ok, "status": self.get_status(), "test": self._test_result}

whiteout_project_provider = WhiteoutProjectProvider()
