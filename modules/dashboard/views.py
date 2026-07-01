"""
WOS-M Dashboard Module
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Dict, Any, List, Optional

from core.bot import WOSMBot
from core.i18n import i18n
from core.database import db
from core.permissions import PermissionLevel, PermissionGuard
from core.audit_log import audit_log, AuditCategory
from views.base import BaseView, PageInfo
from views.buttons import DashboardButton
from views.selects import LanguageSelect


class DashboardView(BaseView):
    """Main dashboard view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("dashboard.title"),
                description=i18n.get("dashboard.description"),
                icon="🎮",
                color=0x3498db
            )
        )
        
        self._build_buttons()
    
    def _build_buttons(self):
        """Build dashboard buttons based on permissions."""
        buttons = [
            ("alliances", i18n.get("dashboard.alliances"), "🏰", 0, discord.ButtonStyle.primary),
            ("players", i18n.get("dashboard.players"), "👥", 0, discord.ButtonStyle.primary),
            ("gift_codes", i18n.get("dashboard.auto_gift"), "🎁", 0, discord.ButtonStyle.success),
            ("events", i18n.get("dashboard.events"), "📅", 1, discord.ButtonStyle.primary),
            ("attendance", i18n.get("dashboard.attendance"), "✅", 1, discord.ButtonStyle.primary),
            ("bear_tracking", i18n.get("dashboard.bear_tracking"), "🐻", 1, discord.ButtonStyle.primary),
            ("ministers", i18n.get("dashboard.ministers"), "👔", 1, discord.ButtonStyle.primary),
            ("notifications", i18n.get("dashboard.notifications"), "🔔", 2, discord.ButtonStyle.primary),
            ("themes", i18n.get("dashboard.themes"), "🎨", 2, discord.ButtonStyle.secondary),
            ("permissions", i18n.get("dashboard.permissions"), "🔐", 2, discord.ButtonStyle.secondary),
            ("maintenance", i18n.get("dashboard.maintenance"), "🔧", 2, discord.ButtonStyle.secondary),
            ("owner_panel", i18n.get("dashboard.owner_panel"), "👑", 3, discord.ButtonStyle.danger),
            ("language", i18n.get("dashboard.language"), "🌐", 3, discord.ButtonStyle.secondary),
            ("settings", i18n.get("dashboard.settings"), "⚙️", 3, discord.ButtonStyle.secondary),
        ]
        
        for btn_id, label, emoji, row, style in buttons:
            # Check if feature is enabled
            from core.feature_registry import feature_registry
            if feature_registry and not feature_registry.is_feature_enabled(btn_id):
                continue
            
            # Check permission
            guard = PermissionGuard(self.bot)
            required_level = PermissionLevel.from_string(
                feature_registry.get_feature(btn_id).required_permission 
                if feature_registry else "member"
            )
            
            # Skip if user doesn't have permission
            if btn_id != "owner_panel" and not guard.has_permission(str(self.user_id), required_level):
                continue
            
            self.add_item(DashboardButton(
                label=label,
                custom_id=f"dash_{btn_id}",
                style=style,
                emoji=emoji,
                row=row
            ))


class LanguageView(BaseView):
    """Language selection view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("language.title"),
                description="",
                icon="🌐",
                color=0x1abc9c
            )
        )
        
        self.add_item(LanguageSelect(i18n.current_locale))
        self.add_back_home_buttons()


async def dashboard_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for dashboard command."""
    view = DashboardView(bot, interaction.user.id)
    
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def language_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for language selection."""
    view = LanguageView(bot, interaction.user.id)
    
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Navigation callbacks
async def nav_back_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate back."""
    await interaction.response.defer()
    # Implementation depends on navigation stack


async def nav_home_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to home (dashboard)."""
    await interaction.response.defer()
    await dashboard_callback(bot, interaction)


# Feature navigation callbacks
async def alliances_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to alliances."""
    from modules.alliances.views import alliances_callback as cb
    await cb(bot, interaction)


async def players_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to players."""
    from modules.players.views import players_callback as cb
    await cb(bot, interaction)


async def gift_codes_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to gift codes."""
    from modules.gift_codes.views import gift_codes_callback as cb
    await cb(bot, interaction)


async def events_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to events."""
    from modules.events.views import events_callback as cb
    await cb(bot, interaction)


async def attendance_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to attendance."""
    from modules.attendance.views import attendance_callback as cb
    await cb(bot, interaction)


async def bear_tracking_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to bear tracking."""
    from modules.bear_tracking.views import bear_tracking_callback as cb
    await cb(bot, interaction)


async def ministers_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to ministers."""
    from modules.ministers.views import ministers_callback as cb
    await cb(bot, interaction)


async def notifications_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to notifications."""
    from modules.notifications.views import notifications_callback as cb
    await cb(bot, interaction)


async def themes_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to themes."""
    from modules.themes.views import themes_callback as cb
    await cb(bot, interaction)


async def permissions_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to permissions."""
    from modules.maintenance.views import permissions_callback as cb
    await cb(bot, interaction)


async def maintenance_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to maintenance."""
    from modules.maintenance.views import maintenance_callback as cb
    await cb(bot, interaction)


async def owner_panel_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to owner panel."""
    from modules.owner_panel.views import owner_panel_callback as cb
    await cb(bot, interaction)


async def settings_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Navigate to settings."""
    from modules.maintenance.views import settings_callback as cb
    await cb(bot, interaction)
