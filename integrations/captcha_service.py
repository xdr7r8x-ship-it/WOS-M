"""
WOS-M Captcha Service
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
import aiohttp
import logging
import base64
from typing import Optional, Dict, Any

from config.settings import settings

logger = logging.getLogger(__name__)


class CaptchaService:
    """Service for solving captchas."""
    
    def __init__(self):
        self.base_url = settings.api.captcha_service_url
        self.timeout = settings.api.request_timeout
    
    async def solve_image_captcha(self, image_data: bytes) -> Optional[str]:
        """
        Solve an image captcha.
        
        Args:
            image_data: Base64 encoded image data
            
        Returns:
            Captcha solution or None
        """
        if not self.base_url:
            logger.warning("Captcha service URL not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/solve/image",
                    json={"image": base64.b64encode(image_data).decode()},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("solution")
                    else:
                        logger.error(f"Captcha solve failed: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("Captcha solve timeout")
            return None
        except Exception as e:
            logger.error(f"Captcha solve error: {e}")
            return None
    
    async def solve_recaptcha(self, site_key: str, site_url: str) -> Optional[str]:
        """
        Solve a reCAPTCHA.
        
        Args:
            site_key: reCAPTCHA site key
            site_url: URL where reCAPTCHA is shown
            
        Returns:
            reCAPTCHA response token
        """
        if not self.base_url:
            logger.warning("Captcha service URL not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/solve/recaptcha",
                    json={"site_key": site_key, "site_url": site_url},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("token")
                    else:
                        logger.error(f"reCAPTCHA solve failed: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("reCAPTCHA solve timeout")
            return None
        except Exception as e:
            logger.error(f"reCAPTCHA solve error: {e}")
            return None
    
    async def solve_hcaptcha(self, site_key: str, site_url: str) -> Optional[str]:
        """
        Solve an hCaptcha.
        
        Args:
            site_key: hCaptcha site key
            site_url: URL where hCaptcha is shown
            
        Returns:
            hCaptcha response token
        """
        if not self.base_url:
            logger.warning("Captcha service URL not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/solve/hcaptcha",
                    json={"site_key": site_key, "site_url": site_url},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("token")
                    else:
                        logger.error(f"hCaptcha solve failed: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("hCaptcha solve timeout")
            return None
        except Exception as e:
            logger.error(f"hCaptcha solve error: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if captcha service is healthy."""
        if not self.base_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except:
            return False


captcha_service = CaptchaService()
