"""
WOS-M Gift Codes Panel
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Dict, Any, List, Optional

from core.bot import WOSMBot
from core.i18n import i18n
from core.database import db
from core.permissions import PermissionLevel, PermissionGuard
from views.base import BaseView, PageInfo, PaginationView
from views.buttons import ActionButton
from views.selects import AllianceSelect, GiftCodeStatusSelect


class GiftCodesPanelView(BaseView):
    """Gift codes panel main view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("gift_codes.title"),
                description="",
                icon="🎁",
                color=0x2ecc71
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add panel buttons."""
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.add_code"),
            custom_id="gift_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.redeem_title"),
            custom_id="gift_redeem",
            style=discord.ButtonStyle.primary,
            emoji="🎁",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.batch_redeem"),
            custom_id="gift_batch",
            style=discord.ButtonStyle.primary,
            emoji="📦",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.auto_redeem"),
            custom_id="gift_auto",
            style=discord.ButtonStyle.success,
            emoji="🤖",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.redeem_alliance"),
            custom_id="gift_alliance",
            style=discord.ButtonStyle.primary,
            emoji="🏰",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.report"),
            custom_id="gift_report",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.code_settings"),
            custom_id="gift_settings",
            style=discord.ButtonStyle.secondary,
            emoji="⚙️",
            row=2
        ))


class GiftCodesListView(PaginationView):
    """Gift codes list view."""
    
    def __init__(self, bot: WOSMBot, user_id: int, status: Optional[str] = None):
        self.bot = bot
        self.status = status
        
        super().__init__(
            user_id=user_id,
            items=[],  # Will be populated
            items_per_page=10,
            page_info=PageInfo(
                title=i18n.get("gift_codes.title"),
                icon="🎁",
                color=0x2ecc71
            )
        )
    
    async def load_codes(self):
        """Load gift codes from database."""
        query = "SELECT * FROM gift_codes"
        params = []
        
        if self.status:
            query += " WHERE status = ?"
            params.append(self.status)
        
        query += " ORDER BY added_at DESC LIMIT 100"
        
        rows = await db.fetchall(query, tuple(params))
        self.items = [dict(row) for row in rows]
        self._total_pages = max(1, (len(self.items) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()


class BatchRedeemView(BaseView):
    """Batch redemption view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("gift_codes.batch_redeem"),
                description="",
                icon="📦",
                color=0x3498db
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    async def _load_alliances(self) -> List[Dict[str, Any]]:
        """Load alliances."""
        rows = await db.fetchall("SELECT id, name FROM alliances WHERE is_active = 1")
        return [dict(row) for row in rows]
    
    def _add_buttons(self):
        """Add action buttons."""
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.redeem_all"),
            custom_id="batch_redeem_all",
            style=discord.ButtonStyle.success,
            emoji="🌐",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.manual_redeem"),
            custom_id="batch_manual",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=1
        ))
