"""
WOS-M Button Views
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Optional, Callable, Dict, Any

from core.i18n import i18n
from core.permissions import PermissionLevel


class DashboardButton(ui.Button):
    """Button for dashboard navigation."""
    
    def __init__(
        self,
        label: str,
        custom_id: str,
        style: discord.ButtonStyle,
        emoji: Optional[str] = None,
        row: int = 0
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style,
            emoji=emoji,
            row=row
        )


class ActionButton(ui.Button):
    """Generic action button."""
    
    def __init__(
        self,
        label: str,
        custom_id: str,
        style: discord.ButtonStyle,
        emoji: Optional[str] = None,
        row: int = 0,
        callback_func: Optional[Callable] = None
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style,
            emoji=emoji,
            row=row
        )
        self.callback_func = callback_func
    
    async def callback(self, interaction: discord.Interaction):
        if self.callback_func:
            await self.callback_func(interaction)


class ToggleButton(ui.Button):
    """Toggle button for enable/disable actions."""
    
    def __init__(
        self,
        label: str,
        custom_id: str,
        is_enabled: bool,
        emoji: Optional[str] = None,
        row: int = 0
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=discord.ButtonStyle.success if is_enabled else discord.ButtonStyle.danger,
            emoji=emoji,
            row=row
        )
        self.is_enabled = is_enabled
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class IconButton(ui.Button):
    """Icon-only button."""
    
    def __init__(
        self,
        emoji: str,
        custom_id: str,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        row: int = 0,
        tooltip: Optional[str] = None
    ):
        super().__init__(
            label="\u200b",  # Zero-width space
            custom_id=custom_id,
            style=style,
            emoji=emoji,
            row=row
        )
        if tooltip:
            self.button_type._underlying.set_tooltip(tooltip)  # type: ignore
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class BackButton(ui.Button):
    """Back navigation button."""
    
    def __init__(self, row: int = 4):
        super().__init__(
            label=i18n.get("buttons.back"),
            custom_id="nav_back",
            style=discord.ButtonStyle.secondary,
            emoji="🔙",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class HomeButton(ui.Button):
    """Home navigation button."""
    
    def __init__(self, row: int = 4):
        super().__init__(
            label=i18n.get("buttons.home"),
            custom_id="nav_home",
            style=discord.ButtonStyle.primary,
            emoji="🏠",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class CloseButton(ui.Button):
    """Close button."""
    
    def __init__(self, row: int = 4):
        super().__init__(
            label=i18n.get("buttons.close"),
            custom_id="nav_close",
            style=discord.ButtonStyle.danger,
            emoji="✖️",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        await interaction.response.defer()


class NavigationButtonGroup(ui.View):
    """Navigation button group with back and home buttons."""
    
    def __init__(self, show_close: bool = False, row: int = 4):
        super().__init__(timeout=300)
        
        self.add_item(BackButton(row=row))
        self.add_item(HomeButton(row=row))
        
        if show_close:
            self.add_item(CloseButton(row=row))


class SelectOptionButton(ui.Button):
    """Button for select menu options."""
    
    def __init__(
        self,
        label: str,
        custom_id: str,
        value: str,
        description: Optional[str] = None,
        emoji: Optional[str] = None,
        row: int = 0
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            row=row
        )
        self.value = value
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class PaginationButton(ui.Button):
    """Pagination button."""
    
    def __init__(
        self,
        direction: str,  # "prev" or "next"
        emoji: str,
        disabled: bool = False,
        row: int = 4
    ):
        label = i18n.get("buttons.previous") if direction == "prev" else i18n.get("buttons.next")
        
        super().__init__(
            label=label,
            custom_id=f"page_{direction}",
            style=discord.ButtonStyle.secondary,
            emoji=emoji,
            row=row,
            disabled=disabled
        )
        self.direction = direction
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class PageIndicator(ui.Button):
    """Page number indicator (disabled button)."""
    
    def __init__(self, current: int, total: int, row: int = 4):
        label = f"{i18n.get('messages.page')} {current} {i18n.get('messages.of')} {total}"
        
        super().__init__(
            label=label,
            custom_id="page_indicator",
            style=discord.ButtonStyle.primary,
            row=row,
            disabled=True
        )


class ActionRowButton(ui.Button):
    """Action row button for inline actions."""
    
    def __init__(
        self,
        label: str,
        custom_id: str,
        style: discord.ButtonStyle,
        emoji: Optional[str] = None,
        row: int = 0
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            style=style,
            emoji=emoji,
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
