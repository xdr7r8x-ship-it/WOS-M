"""
WOS-M Bear Tracking Module
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from typing import Dict, Any, List, Optional

from core.bot import WOSMBot
from core.i18n import i18n
from core.database import db
from core.permissions import PermissionLevel, PermissionGuard
from core.audit_log import audit_log, AuditCategory
from views.base import BaseView, PageInfo
from views.buttons import ActionButton


class BearTrackingView(BaseView):
    """Bear tracking management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("bear_tracking.title"),
                description="",
                icon="🐻",
                color=0x8B4513
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.add_hunt"),
            custom_id="bear_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.damage_record"),
            custom_id="bear_damage",
            style=discord.ButtonStyle.primary,
            emoji="📝",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.leaderboard"),
            custom_id="bear_leaderboard",
            style=discord.ButtonStyle.primary,
            emoji="🏆",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.total_report"),
            custom_id="bear_report",
            style=discord.ButtonStyle.primary,
            emoji="📊",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.ocr_import"),
            custom_id="bear_ocr",
            style=discord.ButtonStyle.secondary,
            emoji="📷",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("bear_tracking.archive_results"),
            custom_id="bear_archive",
            style=discord.ButtonStyle.secondary,
            emoji="📦",
            row=1
        ))


async def bear_tracking_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for bear tracking."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    view = BearTrackingView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_bear_tracking",
        category=AuditCategory.BEAR_TRACKING
    )


async def bear_leaderboard_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for bear leaderboard."""
    rows = await db.fetchall("""
        SELECT p.name, SUM(bdr.damage) as total_damage
        FROM bear_damage_records bdr
        JOIN players p ON bdr.player_id = p.id
        GROUP BY p.id
        ORDER BY total_damage DESC
        LIMIT 20
    """)
    
    embed = discord.Embed(
        title=f"🏆 {i18n.get('bear_tracking.leaderboard')}",
        color=0x8B4513
    )
    
    for i, row in enumerate(rows, 1):
        embed.add_field(
            name=f"{i}. {row['name']}",
            value=f"💥 {row['total_damage']:,}",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# =============================================================================
# Callback stubs for dynamic routing
# Called by bot.py's _route_to_module
# =============================================================================

async def bear_add_callback(bot, interaction):
    """Handle bear_add button."""
    # TODO: Implement bear_add functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def bear_archive_callback(bot, interaction):
    """Handle bear_archive button."""
    # TODO: Implement bear_archive functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def bear_damage_callback(bot, interaction):
    """Handle bear_damage button."""
    # TODO: Implement bear_damage functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def bear_ocr_callback(bot, interaction):
    """Handle bear_ocr button."""
    # TODO: Implement bear_ocr functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def bear_report_callback(bot, interaction):
    """Handle bear_report button."""
    # TODO: Implement bear_report functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

