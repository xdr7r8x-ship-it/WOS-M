"""
WOS-M Players Module
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from typing import Dict, Any, List, Optional

from core.bot import WOSMBot
from core.i18n import i18n
from core.database import db
from core.permissions import PermissionLevel, PermissionGuard
from core.audit_log import audit_log, AuditCategory
from views.base import BaseView, PageInfo, PaginationView
from views.buttons import ActionButton
from views.modals import PlayerModal
from integrations.wos_api_client import wos_api_client


class PlayersView(BaseView):
    """Players management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("players.title"),
                description="",
                icon="👥",
                color=0x3498db
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("players.add_title"),
            custom_id="player_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("players.search_player"),
            custom_id="player_search",
            style=discord.ButtonStyle.primary,
            emoji="🔍",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.view"),
            custom_id="player_list",
            style=discord.ButtonStyle.primary,
            emoji="📋",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("players.sync_data"),
            custom_id="player_sync",
            style=discord.ButtonStyle.secondary,
            emoji="🔄",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("players.move_player"),
            custom_id="player_move",
            style=discord.ButtonStyle.secondary,
            emoji="➡️",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("players.export_players"),
            custom_id="player_export",
            style=discord.ButtonStyle.secondary,
            emoji="📤",
            row=1
        ))


class PlayersListView(PaginationView):
    """Players list view."""
    
    def __init__(self, bot: WOSMBot, user_id: int, alliance_id: Optional[int] = None):
        self.bot = bot
        self.alliance_id = alliance_id
        
        super().__init__(
            user_id=user_id,
            items=[],
            items_per_page=10,
            page_info=PageInfo(
                title=i18n.get("players.title"),
                icon="👥",
                color=0x3498db
            )
        )
    
    async def load_players(self):
        """Load players from database."""
        query = "SELECT p.*, a.name as alliance_name FROM players p LEFT JOIN alliances a ON p.alliance_id = a.id"
        params = []
        
        if self.alliance_id:
            query += " WHERE p.alliance_id = ?"
            params.append(self.alliance_id)
        
        query += " ORDER BY p.name LIMIT 100"
        
        rows = await db.fetchall(query, tuple(params))
        self.items = [dict(row) for row in rows]
        self._total_pages = max(1, (len(self.items) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()


async def players_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for players."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = PlayersView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_players",
        category=AuditCategory.PLAYERS
    )


async def add_player_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for adding player."""
    modal = PlayerModal(mode="add")
    await interaction.response.send_modal(modal)
    
    await modal.wait()
    
    fid = modal.fid_input.value.strip()
    name = modal.name_input.value.strip()
    level = int(modal.level_input.value) if modal.level_input.value else 1
    
    try:
        cursor = await db.execute(
            """INSERT INTO players (fid, name, level) VALUES (?, ?, ?)""",
            (fid, name, level)
        )
        await db.commit()
        player_id = cursor.lastrowid
        
        await interaction.followup.send(
            f"✅ {i18n.get('messages.success')}\n"
            f"**FID:** `{fid}`\n"
            f"**Name:** {name}",
            ephemeral=True
        )
        
        await audit_log.log(
            user_id=str(interaction.user.id),
            user_name=str(interaction.user),
            action="add_player",
            category=AuditCategory.PLAYERS,
            details={"fid": fid, "name": name, "player_id": player_id}
        )
        
    except Exception as e:
        await interaction.followup.send(
            f"❌ {i18n.get('messages.error')}: {str(e)}",
            ephemeral=True
        )


async def list_players_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for listing players."""
    view = PlayersListView(bot, interaction.user.id)
    await view.load_players()
    
    if not view.items:
        await interaction.response.send_message(
            i18n.get("messages.no_results"),
            ephemeral=True
        )
        return
    
    embed = view.create_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def search_player_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for searching player."""
    # Create search modal
    modal = discord.ui.Modal(title=i18n.get("players.search_player"))
    
    fid_input = discord.ui.TextInput(
        label=i18n.get("players.fid"),
        placeholder="Enter FID",
        required=False
    )
    
    name_input = discord.ui.TextInput(
        label=i18n.get("players.player_name"),
        placeholder="Enter player name",
        required=False
    )
    
    modal.add_item(fid_input)
    modal.add_item(name_input)
    
    await interaction.response.send_modal(modal)
    await modal.wait()
    
    query = "SELECT p.*, a.name as alliance_name FROM players p LEFT JOIN alliances a ON p.alliance_id = a.id WHERE 1=1"
    params = []
    
    if fid_input.value:
        query += " AND p.fid LIKE ?"
        params.append(f"%{fid_input.value}%")
    
    if name_input.value:
        query += " AND p.name LIKE ?"
        params.append(f"%{name_input.value}%")
    
    rows = await db.fetchall(query, tuple(params))
    
    if not rows:
        await interaction.followup.send(
            i18n.get("messages.no_results"),
            ephemeral=True
        )
        return
    
    embed = discord.Embed(
        title=f"🔍 {i18n.get('players.search_player')}",
        color=0x3498db
    )
    
    for row in rows[:10]:
        embed.add_field(
            name=row["name"],
            value=f"**FID:** `{row['fid']}`\n"
                  f"**Level:** {row.get('level', 1)}\n"
                  f"**Alliance:** {row.get('alliance_name', 'N/A')}",
            inline=True
        )
    
    await interaction.followup.send(embed=embed, ephemeral=True)


# =============================================================================
# Callback stubs for dynamic routing
# Called by bot.py's _route_to_module
# =============================================================================

async def player_add_callback(bot, interaction):
    """Handle player_add button."""
    # TODO: Implement player_add functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def player_export_callback(bot, interaction):
    """Handle player_export button."""
    # TODO: Implement player_export functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def player_list_callback(bot, interaction):
    """Handle player_list button."""
    # TODO: Implement player_list functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def player_move_callback(bot, interaction):
    """Handle player_move button."""
    # TODO: Implement player_move functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def player_search_callback(bot, interaction):
    """Handle player_search button."""
    # TODO: Implement player_search functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def player_sync_callback(bot, interaction):
    """Handle player_sync button."""
    # TODO: Implement player_sync functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

