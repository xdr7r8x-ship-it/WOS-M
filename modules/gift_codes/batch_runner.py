"""
WOS-M Gift Codes Batch Runner
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable
import logging

from modules.gift_codes.service import gift_code_service
from modules.gift_codes.redemption_engine import redemption_engine
from modules.gift_codes.models import GiftCodeStatus
from core.process_queue import ProcessQueue, QueuePriority

logger = logging.getLogger(__name__)


class BatchRunner:
    """Runner for batch gift code operations."""
    
    def __init__(self, process_queue: ProcessQueue = None):
        self.process_queue = process_queue
        self._running_batches: Dict[int, Dict[str, Any]] = {}
    
    async def queue_batch_redeem(
        self,
        code: str,
        alliance_id: Optional[int] = None,
        player_ids: Optional[List[int]] = None,
        priority: int = QueuePriority.GIFT_REDEEM
    ) -> int:
        """
        Queue a batch redemption for processing.
        
        Args:
            code: Gift code
            alliance_id: Optional alliance ID
            player_ids: Optional specific player IDs
            priority: Queue priority
            
        Returns:
            Task ID from process queue
        """
        task_data = {
            "code": code,
            "alliance_id": alliance_id,
            "player_ids": player_ids
        }
        
        if self.process_queue:
            task_id = await self.process_queue.add_task(
                "gift_redeem",
                task_data,
                priority
            )
            logger.info(f"Queued batch redeem for code {code}, task ID: {task_id}")
            return task_id
        else:
            # Run immediately if no process queue
            result = await redemption_engine.batch_redeem(code, alliance_id, player_ids)
            return result.get("batch_id", 0)
    
    async def queue_validation(
        self,
        code: str,
        priority: int = QueuePriority.GIFT_VALIDATE
    ) -> int:
        """
        Queue code validation.
        
        Args:
            code: Gift code to validate
            priority: Queue priority
            
        Returns:
            Task ID from process queue
        """
        task_data = {"code": code}
        
        if self.process_queue:
            task_id = await self.process_queue.add_task(
                "gift_validate",
                task_data,
                priority
            )
            logger.info(f"Queued validation for code {code}, task ID: {task_id}")
            return task_id
        else:
            # Run immediately
            from modules.gift_codes.validation_engine import validation_engine
            result = await validation_engine.validate_code(code)
            return 1 if result.get("valid") else 0
    
    async def queue_alliance_batch(
        self,
        code: str,
        alliance_id: int
    ) -> int:
        """
        Queue batch redemption for all active alliance players.
        
        Args:
            code: Gift code
            alliance_id: Alliance ID
            
        Returns:
            Task ID
        """
        return await self.queue_batch_redeem(code, alliance_id=alliance_id)
    
    async def queue_global_batch(
        self,
        code: str
    ) -> int:
        """
        Queue batch redemption for all active players across all alliances.
        
        Args:
            code: Gift code
            
        Returns:
            Task ID
        """
        return await self.queue_batch_redeem(code)
    
    async def get_batch_progress(self, batch_id: int) -> Optional[Dict[str, Any]]:
        """
        Get progress of a batch.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            Progress information
        """
        batch = await gift_code_service.get_batch(batch_id)
        
        if not batch:
            return None
        
        progress = {
            "batch_id": batch.id,
            "code": batch.code,
            "total": batch.total_count,
            "success": batch.success_count,
            "failure": batch.failure_count,
            "status": batch.status,
            "started_at": batch.started_at,
            "completed_at": batch.completed_at,
            "progress_percent": (
                ((batch.success_count + batch.failure_count) / batch.total_count * 100)
                if batch.total_count > 0 else 0
            )
        }
        
        return progress
    
    async def cancel_batch(self, batch_id: int) -> bool:
        """
        Cancel a running batch.
        
        Args:
            batch_id: Batch ID
            
        Returns:
            True if cancelled
        """
        if self.process_queue:
            # Cancel related tasks
            await self.process_queue.cancel_task(batch_id)
        
        # Mark batch as cancelled
        await gift_code_service.update_batch(batch_id, status="cancelled")
        
        return True
    
    async def get_all_batches(
        self,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all batches.
        
        Args:
            status: Optional status filter
            limit: Maximum results
            
        Returns:
            List of batches
        """
        query = "SELECT * FROM gift_redemption_batches"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)
        
        rows = await self._db.fetchall(query, tuple(params)) if hasattr(self, '_db') else []
        
        return [
            {
                "id": row["id"],
                "code": row["code"],
                "total": row["total_count"],
                "success": row["success_count"],
                "failure": row["failure_count"],
                "status": row["status"],
                "started_at": row["started_at"],
                "completed_at": row["completed_at"]
            }
            for row in rows
        ]


batch_runner = BatchRunner()
