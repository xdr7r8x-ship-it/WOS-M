"""
WOS-M Gift Codes Redemption Engine
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
from typing import Dict, Any, Optional, List
import logging

from integrations.gift_code_client import gift_code_client, GiftCodeStatus
from integrations.captcha_service import captcha_service
from modules.gift_codes.service import gift_code_service
from modules.gift_codes.models import GiftCodeStatus as ModelStatus
from core.database import db

logger = logging.getLogger(__name__)


class RedemptionEngine:
    """Engine for gift code redemption operations."""
    
    def __init__(self):
        self._captcha_cache: Dict[str, str] = {}
    
    async def redeem_code(self, code: str, player_id: int, player_fid: str = None) -> Dict[str, Any]:
        """
        Redeem a code for a player.
        
        Args:
            code: Gift code
            player_id: Database player ID
            player_fid: Player FID (optional)
            
        Returns:
            Redemption result
        """
        # Get code from database
        gift_code = await gift_code_service.get_code_by_code(code)
        
        if not gift_code:
            return {
                "success": False,
                "error": "code_not_found",
                "message": "Code not found in database"
            }
        
        # Check if already redeemed
        if gift_code.status == ModelStatus.REDEEMED:
            return {
                "success": False,
                "error": "already_redeemed",
                "message": "Code has already been redeemed"
            }
        
        # Check if already redeemed by this player
        if await gift_code_service.check_code_exists(code, player_id):
            return {
                "success": False,
                "error": "already_redeemed_by_player",
                "message": "You have already redeemed this code"
            }
        
        # Get FID if not provided
        if not player_fid:
            row = await db.fetchone("SELECT fid FROM players WHERE id = ?", (player_id,))
            if row:
                player_fid = row["fid"]
        
        if not player_fid:
            return {
                "success": False,
                "error": "no_fid",
                "message": "Player FID not found"
            }
        
        # Update status to redeeming
        await gift_code_service.update_code_status(gift_code.id, ModelStatus.REDEEMING)
        
        # Check for captcha requirement
        captcha_token = None
        # if self._requires_captcha(code):
        #     captcha_token = await self._solve_captcha()
        #     if not captcha_token:
        #         await gift_code_service.update_code_status(gift_code.id, ModelStatus.FAILED)
        #         return {
        #             "success": False,
        #             "error": "captcha_failed",
        #             "message": "Failed to solve captcha"
        #         }
        
        # Attempt redemption
        try:
            result = await gift_code_client.redeem_code(code, player_fid)
            
            status = GiftCodeStatus(result.get("status", "failed"))
            
            if status == GiftCodeStatus.REDEEMED:
                # Success
                await gift_code_service.update_code_status(gift_code.id, ModelStatus.REDEEMED)
                await gift_code_service.add_redemption(
                    gift_code.id, player_id, ModelStatus.REDEEMED.value
                )
                
                return {
                    "success": True,
                    "status": ModelStatus.REDEEMED,
                    "rewards": result.get("rewards", [])
                }
            
            else:
                # Failed
                await gift_code_service.update_code_status(gift_code.id, ModelStatus(status.value))
                await gift_code_service.add_redemption(
                    gift_code.id, player_id, status.value,
                    error_message=result.get("error")
                )
                
                return {
                    "success": False,
                    "status": ModelStatus(status.value),
                    "error": result.get("error"),
                    "message": f"Redemption failed: {result.get('error')}"
                }
                
        except Exception as e:
            logger.error(f"Error redeeming code {code} for player {player_id}: {e}")
            await gift_code_service.update_code_status(gift_code.id, ModelStatus.FAILED)
            
            return {
                "success": False,
                "error": "redemption_error",
                "message": str(e)
            }
    
    async def batch_redeem(
        self,
        code: str,
        alliance_id: int = None,
        player_ids: List[int] = None
    ) -> Dict[str, Any]:
        """
        Batch redeem a code for multiple players.
        
        Args:
            code: Gift code
            alliance_id: Alliance ID (if redeeming for alliance)
            player_ids: List of player IDs (if specific players)
            
        Returns:
            Batch result
        """
        # Create batch
        batch_id = await gift_code_service.create_batch(code, alliance_id)
        
        # Get players
        if player_ids is None:
            if alliance_id:
                rows = await db.fetchall(
                    "SELECT id, fid, name FROM players WHERE alliance_id = ? AND is_active = 1",
                    (alliance_id,)
                )
            else:
                rows = await db.fetchall(
                    "SELECT id, fid, name FROM players WHERE is_active = 1"
                )
            player_ids = [row["id"] for row in rows]
            players_info = {row["id"]: {"fid": row["fid"], "name": row["name"]} for row in rows}
        else:
            rows = await db.fetchall(
                "SELECT id, fid, name FROM players WHERE id IN ({})".format(
                    ",".join("?" * len(player_ids))
                ),
                tuple(player_ids)
            )
            players_info = {row["id"]: {"fid": row["fid"], "name": row["name"]} for row in rows}
        
        total = len(player_ids)
        await gift_code_service.update_batch(batch_id, total=total, status="processing")
        
        success_count = 0
        failure_count = 0
        
        for player_id in player_ids:
            player_info = players_info.get(player_id, {})
            
            result = await self.redeem_code(
                code,
                player_id,
                player_fid=player_info.get("fid")
            )
            
            if result["success"]:
                success_count += 1
                status = ModelStatus.REDEEMED.value
            else:
                failure_count += 1
                status = ModelStatus.FAILED.value
            
            await gift_code_service.add_batch_result(
                batch_id=batch_id,
                player_id=player_id,
                player_name=player_info.get("name", "Unknown"),
                status=status,
                error_message=result.get("error")
            )
            
            # Update batch progress
            await gift_code_service.update_batch(
                batch_id,
                success=success_count,
                failure=failure_count
            )
            
            # Rate limiting
            await asyncio.sleep(0.2)
        
        # Mark batch as completed
        await gift_code_service.update_batch(
            batch_id,
            status="completed",
            success=success_count,
            failure=failure_count
        )
        
        return {
            "batch_id": batch_id,
            "code": code,
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "status": "completed"
        }
    
    async def retry_failed_redemptions(self) -> Dict[str, Any]:
        """Retry all failed/unconfirmed redemptions."""
        rows = await db.fetchall(
            """SELECT * FROM gift_codes 
               WHERE status IN ('failed', 'pending', 'redeeming') 
               AND datetime(added_at, '+1 hour') < datetime('now')"""
        )
        
        retried = 0
        succeeded = 0
        
        for row in rows:
            code = row["code"]
            code_id = row["id"]
            
            # Get players who need to retry
            redemption_rows = await db.fetchall(
                """SELECT * FROM gift_redemptions 
                   WHERE code_id = ? AND status != 'redeemed'""",
                (code_id,)
            )
            
            for redemption in redemption_rows:
                result = await self.redeem_code(code, redemption["player_id"])
                
                if result["success"]:
                    succeeded += 1
                
                retried += 1
            
            await asyncio.sleep(1)  # Rate limiting
        
        return {
            "retried": retried,
            "succeeded": succeeded
        }
    
    def _requires_captcha(self, code: str) -> bool:
        """Check if code requires captcha solving."""
        # This would be based on game API response
        return False


redemption_engine = RedemptionEngine()
