"""
WOS-M OCR Service
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
import aiohttp
import logging
import base64
from typing import Optional, Dict, Any, List

from config.settings import settings

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR (Optical Character Recognition)."""
    
    def __init__(self):
        self.base_url = settings.api.ocr_service_url
        self.timeout = settings.api.request_timeout * 2  # OCR needs more time
    
    async def extract_text(self, image_data: bytes) -> Optional[str]:
        """
        Extract text from an image.
        
        Args:
            image_data: Image data in bytes
            
        Returns:
            Extracted text or None
        """
        if not self.base_url:
            logger.warning("OCR service URL not configured")
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/extract",
                    json={"image": base64.b64encode(image_data).decode()},
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("text")
                    else:
                        logger.error(f"OCR extract failed: HTTP {response.status}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("OCR extract timeout")
            return None
        except Exception as e:
            logger.error(f"OCR extract error: {e}")
            return None
    
    async def extract_bear_damage(self, image_data: bytes) -> List[Dict[str, Any]]:
        """
        Extract bear damage data from an image.
        
        Args:
            image_data: Image data containing bear damage screenshot
            
        Returns:
            List of player damage records
        """
        text = await self.extract_text(image_data)
        
        if not text:
            return []
        
        # Parse the extracted text to extract damage records
        # Expected format: "PlayerName DamageValue" per line
        records = []
        lines = text.strip().split("\n")
        
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                # Try to find a number at the end (damage value)
                try:
                    damage = int(parts[-1].replace(",", ""))
                    player_name = " ".join(parts[:-1])
                    records.append({
                        "player_name": player_name,
                        "damage": damage
                    })
                except ValueError:
                    # Last part is not a number, try another approach
                    continue
        
        return records
    
    async def extract_attendance(self, image_data: bytes) -> Dict[str, List[str]]:
        """
        Extract attendance data from an image.
        
        Args:
            image_data: Image data containing attendance screenshot
            
        Returns:
            Dictionary with present and absent player lists
        """
        text = await self.extract_text(image_data)
        
        if not text:
            return {"present": [], "absent": []}
        
        # This would need custom parsing based on the game screenshot format
        # Placeholder implementation
        present = []
        absent = []
        
        lines = text.strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for present/absent markers in the text
            lower_line = line.lower()
            if "present" in lower_line or "✅" in line or "+" in line:
                present.append(line)
            elif "absent" in lower_line or "❌" in line or "-" in line:
                absent.append(line)
            else:
                # Default to present if unclear
                present.append(line)
        
        return {"present": present, "absent": absent}
    
    async def health_check(self) -> bool:
        """Check if OCR service is healthy."""
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


ocr_service = OCRService()
