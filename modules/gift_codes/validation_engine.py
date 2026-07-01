"""
WOS-M Gift Codes Validation Engine
© MANSOUR — WOS-M. All rights reserved.
"""
import re
from typing import Dict, Any, Optional
import logging

from integrations.gift_code_client import gift_code_client, GiftCodeStatus

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Engine for validating gift codes."""
    
    CODE_PATTERN = re.compile(r'^[A-Z0-9]{6,32}$')
    
    async def validate_code_format(self, code: str) -> Dict[str, Any]:
        """
        Validate the format of a gift code.
        
        Args:
            code: The gift code to validate
            
        Returns:
            Validation result
        """
        if not code:
            return {
                "valid": False,
                "error": "empty_code",
                "message": "Code cannot be empty"
            }
        
        code = code.strip().upper()
        
        if len(code) < 6:
            return {
                "valid": False,
                "error": "code_too_short",
                "message": "Code is too short (minimum 6 characters)"
            }
        
        if len(code) > 32:
            return {
                "valid": False,
                "error": "code_too_long",
                "message": "Code is too long (maximum 32 characters)"
            }
        
        if not self.CODE_PATTERN.match(code):
            return {
                "valid": False,
                "error": "invalid_format",
                "message": "Code contains invalid characters"
            }
        
        return {
            "valid": True,
            "code": code,
            "error": None,
            "message": "Code format is valid"
        }
    
    async def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate a gift code (format + API check).
        
        Args:
            code: The gift code to validate
            
        Returns:
            Validation result with status
        """
        # First validate format
        format_result = await self.validate_code_format(code)
        
        if not format_result["valid"]:
            return {
                "valid": False,
                "status": GiftCodeStatus.INVALID,
                **format_result
            }
        
        # Then validate via API
        try:
            api_result = await gift_code_client.validate_code(code)
            
            return {
                "valid": True,
                "code": format_result["code"],
                "status": GiftCodeStatus(api_result.get("status", "invalid")),
                "rewards": api_result.get("rewards", []),
                "expires_at": api_result.get("expires_at"),
                "error": api_result.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error validating code {code}: {e}")
            return {
                "valid": False,
                "code": format_result["code"],
                "status": GiftCodeStatus.INVALID,
                "error": "validation_error",
                "message": str(e)
            }
    
    async def batch_validate(self, codes: list) -> Dict[str, Dict[str, Any]]:
        """
        Validate multiple codes.
        
        Args:
            codes: List of codes to validate
            
        Returns:
            Dictionary mapping code to validation result
        """
        results = {}
        
        for code in codes:
            results[code] = await self.validate_code(code)
        
        return results


validation_engine = ValidationEngine()
