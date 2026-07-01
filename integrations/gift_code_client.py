"""
WOS-M Gift Code Client
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)


class GiftCodeStatus:
    """Gift code status constants."""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    REDEEMING = "redeeming"
    REDEEMED = "redeemed"
    ALREADY_REDEEMED = "already_redeemed"
    FAILED = "failed"


class GiftCodeClient:
    """Client for interacting with gift code redemption API."""
    
    def __init__(self):
        self.base_url = settings.api.gift_code_api_base_url
        self.timeout = settings.api.request_timeout
    
    async def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate a gift code.
        
        Args:
            code: Gift code to validate
            
        Returns:
            Validation result with status
        """
        if not self.base_url:
            logger.warning("Gift code API base URL not configured")
            return {"status": GiftCodeStatus.INVALID, "error": "API not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/validate/{code}",
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": data.get("status", GiftCodeStatus.VALID),
                            "rewards": data.get("rewards", []),
                            "expires_at": data.get("expires_at")
                        }
                    elif response.status == 404:
                        return {"status": GiftCodeStatus.INVALID}
                    elif response.status == 410:
                        return {"status": GiftCodeStatus.EXPIRED}
                    elif response.status == 409:
                        return {"status": GiftCodeStatus.ALREADY_REDEEMED}
                    else:
                        return {"status": GiftCodeStatus.INVALID, "error": f"HTTP {response.status}"}
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout validating code {code}")
            return {"status": GiftCodeStatus.PENDING, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Error validating code {code}: {e}")
            return {"status": GiftCodeStatus.INVALID, "error": str(e)}
    
    async def redeem_code(self, code: str, fid: str) -> Dict[str, Any]:
        """
        Redeem a gift code for a player.
        
        Args:
            code: Gift code
            fid: Player FID
            
        Returns:
            Redemption result
        """
        if not self.base_url:
            logger.warning("Gift code API base URL not configured")
            return {"status": GiftCodeStatus.FAILED, "error": "API not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/redeem",
                    json={"code": code, "fid": fid},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": GiftCodeStatus.REDEEMED,
                            "rewards": data.get("rewards", [])
                        }
                    elif response.status == 400:
                        return {"status": GiftCodeStatus.INVALID, "error": "Invalid code or FID"}
                    elif response.status == 409:
                        return {"status": GiftCodeStatus.ALREADY_REDEEMED}
                    elif response.status == 410:
                        return {"status": GiftCodeStatus.EXPIRED}
                    else:
                        return {"status": GiftCodeStatus.FAILED, "error": f"HTTP {response.status}"}
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout redeeming code {code} for {fid}")
            return {"status": GiftCodeStatus.FAILED, "error": "Timeout"}
        except Exception as e:
            logger.error(f"Error redeeming code {code} for {fid}: {e}")
            return {"status": GiftCodeStatus.FAILED, "error": str(e)}
    
    async def batch_validate(self, codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Validate multiple codes at once.
        
        Args:
            codes: List of codes to validate
            
        Returns:
            Dictionary mapping code to validation result
        """
        results = {}
        
        for code in codes:
            results[code] = await self.validate_code(code)
            await asyncio.sleep(0.1)  # Rate limiting
        
        return results
    
    async def batch_redeem(self, code: str, fids: List[str]) -> Dict[str, Any]:
        """
        Redeem a code for multiple players.
        
        Args:
            code: Gift code
            fids: List of player FIDs
            
        Returns:
            Batch redemption results
        """
        results = {
            "code": code,
            "total": len(fids),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for fid in fids:
            result = await self.redeem_code(code, fid)
            
            if result.get("status") == GiftCodeStatus.REDEEMED:
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "fid": fid,
                "status": result.get("status"),
                "error": result.get("error")
            })
            
            await asyncio.sleep(0.2)  # Rate limiting
        
        return results
    
    async def health_check(self) -> bool:
        """Check if API is healthy."""
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


gift_code_client = GiftCodeClient()
