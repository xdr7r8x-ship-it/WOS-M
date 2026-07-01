"""
WOS-M Alliances Module
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
from views.base import BaseView, PageInfo, PaginationView
from views.buttons import ActionButton
from views.modals import AllianceModal


class AlliancesView(BaseView):
    """Alliances management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("alliances.title"),
                description="",
                icon="🏰",
                color=0x3498db
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("buttons.add"),
            custom_id="alliance_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.view"),
            custom_id="alliance_list",
            style=discord.ButtonStyle.primary,
            emoji="📋",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.edit"),
            custom_id="alliance_edit",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.delete"),
            custom_id="alliance_delete",
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("alliances.sync_settings"),
            custom_id="alliance_sync_settings",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("alliances.gift_settings"),
            custom_id="alliance_gift_settings",
            style=discord.ButtonStyle.secondary,
            emoji="🎁",
            row=1
        ))


class AllianceListView(PaginationView):
    """Alliance list view with pagination."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        
        super().__init__(
            user_id=user_id,
            items=[],  # Will be populated by load_alliances
            items_per_page=10,
            page_info=PageInfo(
                title=i18n.get("alliances.title"),
                icon="🏰",
                color=0x3498db
            )
        )
    
    async def _fetch_alliances(self) -> List[Dict[str, Any]]:
        """Fetch all alliances."""
        rows = await db.fetchall("SELECT * FROM alliances ORDER BY name")
        return [dict(row) for row in rows]
    
    def create_alliance_embed(self, alliance: Dict[str, Any]) -> discord.Embed:
        """Create alliance info embed."""
        status = i18n.get("alliances.status_active") if alliance.get("is_active") else i18n.get("alliances.status_inactive")
        
        embed = discord.Embed(
            title=f"{alliance.get('name', 'Unknown')}",
            color=0x3498db
        )
        
        embed.add_field(
            name=i18n.get("alliances.name"),
            value=alliance.get("name", "N/A"),
            inline=True
        )
        
        embed.add_field(
            name=i18n.get("alliances.state_kid"),
            value=alliance.get("state_kid", "N/A"),
            inline=True
        )
        
        embed.add_field(
            name="Status",
            value=status,
            inline=True
        )
        
        return embed


async def alliances_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for alliances."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = AlliancesView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_alliances",
        category=AuditCategory.ALLIANCES
    )


async def add_alliance_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for adding alliance."""
    modal = AllianceModal(mode="add")
    await interaction.response.send_modal(modal)
    
    await modal.wait()
    
    name = modal.name_input.value
    state_kid = modal.state_kid_input.value
    discord_guild = modal.discord_server_input.value
    
    await db.execute(
        """INSERT INTO alliances (name, state_kid, discord_guild_id) 
           VALUES (?, ?, ?)""",
        (name, state_kid, discord_guild)
    )
    await db.commit()
    
    await interaction.followup.send(
        i18n.get("messages.success"),
        ephemeral=True
    )
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="add_alliance",
        category=AuditCategory.ALLIANCES,
        details={"name": name, "state_kid": state_kid}
    )


async def list_alliances_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for listing alliances."""
    rows = await db.fetchall("SELECT * FROM alliances ORDER BY name")
    
    if not rows:
        await interaction.response.send_message(
            i18n.get("messages.no_results"),
            ephemeral=True
        )
        return
    
    view = AllianceListView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# =============================================================================
# Callback stubs for dynamic routing
# These are called by bot.py's _route_to_module
# =============================================================================

async def alliance_add_callback(bot, interaction):
    """Handle alliance_add button."""
    await alliances_callback(bot, interaction)


async def alliance_list_callback(bot, interaction):
    """Handle alliance_list button."""
    await alliances_callback(bot, interaction)


async def alliance_edit_callback(bot, interaction):
    """Handle alliance_edit button."""
    await alliances_callback(bot, interaction)


async def alliance_delete_callback(bot, interaction):
    """Handle alliance_delete button."""
    await alliances_callback(bot, interaction)


async def alliance_sync_settings_callback(bot, interaction):
    """Handle alliance_sync_settings button."""
    await alliances_callback(bot, interaction)


async def alliance_gift_settings_callback(bot, interaction):
    """Handle alliance_gift_settings button."""
    await alliances_callback(bot, interaction)


async def alliance_redeem_modal_callback(bot, interaction):
    """Handle alliance_redeem_modal button."""
    await alliances_callback(bot, interaction)


async def alliance_select_callback(bot, interaction):
    """Handle alliance_select from select menu."""
    if interaction.data.get("values"):
        selected_id = interaction.data["values"][0]
        # TODO: Handle alliance selection
        await interaction.response.send_message(
            f"✅ Selected alliance: {selected_id}",
            ephemeral=True
        )
