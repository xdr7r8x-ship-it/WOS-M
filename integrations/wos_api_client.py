"""
WOS-M WOS API Client
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib

from config.settings import settings

logger = logging.getLogger(__name__)


class WOSAPIClient:
    """Client for interacting with WOS game API."""
    
    def __init__(self):
        self.base_url = settings.api.wos_api_base_url
        self.timeout = settings.api.request_timeout
        self.rate_limit_calls = settings.api.rate_limit_calls
        self.rate_limit_period = settings.api.rate_limit_period
        self._cache: Dict[str, tuple] = {}
        self._rate_limiter_lock = asyncio.Lock()
        self._last_request_time = {}
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make an API request with rate limiting and retry logic."""
        if not self.base_url:
            logger.warning("WOS API base URL not configured")
            return None
        
        # Rate limiting
        await self._check_rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        for retry in range(3):
            try:
                async with aiohttp.ClientSession() as session:
                    kwargs = {"timeout": aiohttp.ClientTimeout(total=self.timeout)}
                    
                    if method.upper() == "GET":
                        async with session.get(url, params=params, **kwargs) as response:
                            return await self._handle_response(response)
                    elif method.upper() == "POST":
                        async with session.post(url, json=data, **kwargs) as response:
                            return await self._handle_response(response)
                            
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout for {endpoint}, retry {retry + 1}")
                if retry == 2:
                    return {"error": "timeout", "message": "Request timed out"}
            except aiohttp.ClientError as e:
                logger.warning(f"Request error for {endpoint}: {e}, retry {retry + 1}")
                await asyncio.sleep(2 ** retry)
            except Exception as e:
                logger.error(f"Unexpected error for {endpoint}: {e}")
                return {"error": "server_error", "message": str(e)}
        
        return {"error": "failed_after_retries"}
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle API response."""
        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            return {"error": "unauthorized", "message": "Invalid API credentials"}
        elif response.status == 429:
            return {"error": "rate_limit", "message": "Rate limit exceeded"}
        elif response.status == 404:
            return {"error": "not_found", "message": "Resource not found"}
        else:
            text = await response.text()
            return {"error": "server_error", "message": f"HTTP {response.status}: {text}"}
    
    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        async with self._rate_limiter_lock:
            now = datetime.now()
            current_minute = now.replace(second=0, microsecond=0)
            
            if current_minute in self._last_request_time:
                count = self._last_request_time[current_minute]
                if count >= self.rate_limit_calls:
                    wait_time = 60 - now.second
                    logger.debug(f"Rate limit reached, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
            
            self._last_request_time = {
                k: v for k, v in self._last_request_time.items()
                if k >= current_minute - timedelta(minutes=1)
            }
            
            self._last_request_time[current_minute] = \
                self._last_request_time.get(current_minute, 0) + 1
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """Generate cache key."""
        param_str = str(sorted(params.items())) if params else ""
        return hashlib.md5(f"{endpoint}:{param_str}".encode()).hexdigest()
    
    async def _get_cached(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        cache_time: int = 300
    ) -> Optional[Dict[str, Any]]:
        """Get cached response if still valid."""
        cache_key = self._get_cache_key(endpoint, params)
        
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=cache_time):
                return cached_data
        
        return None
    
    async def _set_cache(self, endpoint: str, params: Optional[Dict], data: Dict[str, Any]):
        """Set cache for response."""
        cache_key = self._get_cache_key(endpoint, params)
        self._cache[cache_key] = (datetime.now(), data)
    
    async def get_player_data(self, fid: str) -> Optional[Dict[str, Any]]:
        """
        Get player data by FID.
        
        Args:
            fid: Player's FID
            
        Returns:
            Player data dictionary or None
        """
        cache_key = f"player:{fid}"
        
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=300):
                return cached_data
        
        result = await self._make_request("GET", f"/player/{fid}")
        
        if result and "error" not in result:
            self._cache[cache_key] = (datetime.now(), result)
        
        return result
    
    async def player_exists(self, fid: str) -> bool:
        """Check if player exists."""
        result = await self.get_player_data(fid)
        return result is not None and "error" not in result
    
    async def get_player_name(self, fid: str) -> Optional[str]:
        """Get player name by FID."""
        data = await self.get_player_data(fid)
        if data:
            return data.get("name")
        return None
    
    async def get_player_alliance(self, fid: str) -> Optional[str]:
        """Get player alliance by FID."""
        data = await self.get_player_data(fid)
        if data:
            return data.get("alliance")
        return None
    
    async def get_player_state_kid(self, fid: str) -> Optional[str]:
        """Get player State/KID by FID."""
        data = await self.get_player_data(fid)
        if data:
            return data.get("state_kid")
        return None
    
    async def get_player_level(self, fid: str) -> int:
        """Get player level by FID."""
        data = await self.get_player_data(fid)
        if data:
            return data.get("level", 1)
        return 1
    
    async def sync_alliance(self, state_kid: str) -> Optional[Dict[str, Any]]:
        """Sync alliance data."""
        result = await self._make_request("GET", f"/alliance/{state_kid}")
        return result
    
    async def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            result = await self._make_request("GET", "/health")
            return result is not None and "error" not in result
        except:
            return False


wos_api_client = WOSAPIClient()
