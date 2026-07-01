"""
WOS-M WhiteoutProject Provider - Real Gift Code Redemption
Based on: https://github.com/whiteout-project/bot

Real redemption path:
1. /api/player - Player lookup
2. /api/captcha - Fetch CAPTCHA
3. ONNX OCR solve (primary) / ddddocr (fallback)
4. /api/gift_code - Redeem
"""
import asyncio, hashlib, time, ssl, certifi, aiohttp, base64, random, logging
from typing import Optional, Dict, Any, Tuple, List
from dataclasses import dataclass
from enum import Enum

from config.settings import settings
from integrations.browser_headers import get_headers
from integrations.captcha.onnx_captcha_solver import OnnxCaptchaSolver

logger = logging.getLogger(__name__)

class RedemptionStatus(Enum):
    SUCCESS = "SUCCESS"; RECEIVED = "RECEIVED"; SAME_TYPE_EXCHANGE = "SAME TYPE EXCHANGE"
    TOO_POOR_SPEND_MORE = "TOO_POOR_SPEND_MORE"; TOO_SMALL_SPEND_MORE = "TOO_SMALL_SPEND_MORE"
    TIME_ERROR = "TIME_ERROR"; CDK_NOT_FOUND = "CDK_NOT_FOUND"; USAGE_LIMIT = "USAGE_LIMIT"
    NOT_LOGIN = "NOT_LOGIN"; UNAUTHORIZED = "UNAUTHORIZED"; LOGIN_FAILED = "LOGIN_FAILED"
    CAPTCHA_ERROR = "CAPTCHA_ERROR"; CAPTCHA_INVALID = "CAPTCHA_INVALID"
    CAPTCHA_TOO_FREQUENT = "CAPTCHA_TOO_FREQUENT"; CAPTCHA_FETCH_ERROR = "CAPTCHA_FETCH_ERROR"
    CAPTCHA_INVALID_AFTER_RETRIES = "CAPTCHA_INVALID_AFTER_RETRIES"; CAPTCHA_EXPIRED = "CAPTCHA_EXPIRED"
    SOLVER_ERROR = "SOLVER_ERROR"; OCR_DISABLED = "OCR_DISABLED"
    ONNX_SOLVER_ERROR = "ONNX_SOLVER_ERROR"; ONNX_MODEL_MISSING = "ONNX_MODEL_MISSING"
    LOW_CONFIDENCE_CAPTCHA = "LOW_CONFIDENCE_CAPTCHA"
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
    MAX_CAPTCHA_ATTEMPTS = 5; CAPTCHA_BACKOFF = (60, 90)

    def __init__(self):
        self._session = None
        self._captcha_solver = None
        self._onnx_available = False
        self._ddddocr_fallback = None
        self._ddddocr_ok = False
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
        # Initialize ONNX captcha solver (primary)
        try:
            self._captcha_solver = OnnxCaptchaSolver()
            self._onnx_available = self._captcha_solver.is_onnx_available()
            logger.info(f"ONNX Captcha solver initialized: {self._onnx_available}")
        except Exception as e:
            logger.warning(f"ONNX solver init failed: {e}")
            self._captcha_solver = None
            self._onnx_available = False
        
        # Initialize ddddocr (fallback only)
        try:
            import ddddocr
            self._ddddocr_fallback = ddddocr.DdddOcr(show_ad=False)
            self._ddddocr_ok = True
            logger.info("ddddocr fallback initialized")
        except:
            self._ddddocr_fallback = None
            self._ddddocr_ok = False

    def is_configured(self): return bool(self.api_key or self.login_token or self.cookie or self.session_id)
    def is_enabled(self): return self._enabled
    def get_status(self):
        if self._enabled: return f"Enabled ({self.provider_name})"
        elif self.is_configured(): return f"Configured - {self._test_result or 'Unknown'}"
        return "Locked - Missing credentials"
    def has_ocr(self): return self._onnx_available or self._ddddocr_ok
    def has_onnx(self): return self._onnx_available

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

    async def solve_captcha(self, img, fid=None, attempt=0):
        """Solve captcha using ONNX (primary) or ddddocr (fallback)."""
        if not self.has_ocr(): return None, False, "NONE", 0.0
        
        if self._onnx_available and self._captcha_solver:
            try:
                result, success, method, confidence, _ = await self._captcha_solver.solve_captcha(img, fid=fid, attempt=attempt)
                if success and result: return result, True, method, confidence
                logger.warning(f"ONNX solve failed, trying ddddocr fallback")
            except Exception as e:
                logger.warning(f"ONNX error: {e}")
        
        if self._ddddocr_ok and self._ddddocr_fallback:
            try:
                result = await asyncio.to_thread(self._ddddocr_fallback.classification, img)
                if result: return result, True, "DDDDOCR", 0.75
            except Exception as e:
                logger.error(f"ddddocr error: {e}")
        
        return None, False, "NONE", 0.0

    async def redeem(self, code, fid):
        await self.init()
        ok, pinfo, err = await self.get_player(fid)
        if not ok:
            if err == "NOT_LOGIN": return RedeemResult(RedemptionStatus.NOT_LOGIN, "API requires login", pinfo)
            if err == "UNAUTHORIZED": return RedeemResult(RedemptionStatus.UNAUTHORIZED, "API requires auth", pinfo)
            return RedeemResult(RedemptionStatus.ERROR, f"Player lookup failed: {err}", pinfo)
        
        if not self.has_ocr(): return RedeemResult(RedemptionStatus.OCR_DISABLED, "No OCR available", pinfo)
        
        last_error = None
        for captcha_attempt in range(self.MAX_CAPTCHA_ATTEMPTS):
            ok, cap, err = await self.fetch_captcha(fid)
            if not ok or cap is None:
                if err == "NOT_LOGIN": return RedeemResult(RedemptionStatus.NOT_LOGIN, "CAPTCHA requires login", pinfo)
                if "TOO_FREQUENT" in err:
                    backoff_min, backoff_max = self.CAPTCHA_BACKOFF
                    wait = random.uniform(backoff_min, backoff_max)
                    logger.warning(f"CAPTCHA rate limited, backing off {wait:.1f}s")
                    await asyncio.sleep(wait)
                    continue
                return RedeemResult(RedemptionStatus.CAPTCHA_FETCH_ERROR, f"CAPTCHA failed: {err}", pinfo)
            
            captcha_text, solved, method, confidence = await self.solve_captcha(cap, fid=fid, attempt=captcha_attempt)
            
            if not solved or not captcha_text:
                logger.warning(f"Captcha solve failed (attempt {captcha_attempt + 1})")
                last_error = RedemptionStatus.SOLVER_ERROR
                continue
            
            if method == "ONNX" and confidence < 0.60:
                logger.warning(f"Low confidence ({confidence:.3f}), retrying with new captcha")
                last_error = RedemptionStatus.LOW_CONFIDENCE_CAPTCHA
                continue
            
            await self._wait_rate(1)
            now = int(time.time()*1000); params = {"captcha_code": captcha_text, "cdk": code, "fid": fid, "time": now}
            sign = self._sign(params)
            
            for _ in range(self.MAX_RETRIES):
                try:
                    async with self._session.post(self.API_REDEEM, headers=self._hdrs(self.API_BASE),
                        data={"cdk": code, "fid": fid, "time": now, "captcha_code": captcha_text, "sign": sign},
                        timeout=aiohttp.ClientTimeout(total=30)) as r:
                            try: res = await r.json()
                            except: return RedeemResult(RedemptionStatus.ERROR, "Invalid response", pinfo)
                            
                            err_code = res.get("err_code"); msg = res.get("msg", "")
                            
                            if err_code == 40103:
                                logger.warning("CAPTCHA rejected, retrying with new captcha")
                                last_error = RedemptionStatus.CAPTCHA_INVALID
                                break
                            
                            if err_code == 40102:
                                logger.warning("Captcha expired, fetching new one")
                                last_error = RedemptionStatus.CAPTCHA_EXPIRED
                                break
                            
                            m = {20000: (RedemptionStatus.SUCCESS, "Claimed"),
                                 40008: (RedemptionStatus.RECEIVED, "Already claimed"),
                                 40014: (RedemptionStatus.CDK_NOT_FOUND, "Code not found"),
                                 40007: (RedemptionStatus.TIME_ERROR, "Expired"),
                                 40005: (RedemptionStatus.USAGE_LIMIT, "Fully claimed"),
                                 40009: (RedemptionStatus.NOT_LOGIN, "NOT LOGIN")}
                            
                            if err_code in m:
                                s, t = m[err_code]
                                return RedeemResult(s, t, pinfo, res)
                            
                            if msg == "success": return RedeemResult(RedemptionStatus.SUCCESS, "Claimed", pinfo, res)
                            
                            return RedeemResult(RedemptionStatus.UNKNOWN_API_RESPONSE, f"err={err_code}", pinfo, res)
                except asyncio.TimeoutError: await asyncio.sleep(self.RETRY_DELAY)
                except: await asyncio.sleep(self.RETRY_DELAY)
            
            if last_error in [RedemptionStatus.CAPTCHA_INVALID, RedemptionStatus.CAPTCHA_EXPIRED]:
                await asyncio.sleep(1)
                continue
        
        return RedeemResult(RedemptionStatus.CAPTCHA_INVALID_AFTER_RETRIES, 
            f"Failed after {self.MAX_CAPTCHA_ATTEMPTS} captcha attempts", pinfo)

    def info(self): return {
        "name": self.provider_name, "enabled": self._enabled, "configured": self.is_configured(),
        "ocr": self.has_ocr(), "onnx": self.has_onnx(), "ddddocr": self._ddddocr_ok,
        "status": self.get_status(), "test": self._test_result}

whiteout_project_provider = WhiteoutProjectProvider()