"""
WOS-M Button Views
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Optional, Callable, Dict, Any

from core.i18n import i18n
from core.permissions import PermissionLevel


def get_bot_from_view_or_interaction(interaction: discord.Interaction):
    """Get bot instance from view or interaction."""
    view = interaction.message.components[0].parent if interaction.message and interaction.message.components else None
    if view and hasattr(view, 'bot'):
        return view.bot
    return interaction.client


class RoutedButton(ui.Button):
    """Base button that routes to dispatcher for all custom_id buttons."""

    async def callback(self, interaction: discord.Interaction):
        """Route all button clicks through the dispatcher."""
        from core.bot import dispatch_registered_interaction
        bot = interaction.client
        await dispatch_registered_interaction(bot, interaction)


class DashboardButton(RoutedButton):
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


class ActionButton(RoutedButton):
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
        """Route to dispatcher, with optional callback_func as override."""
        if self.callback_func:
            await self.callback_func(interaction)
        else:
            await super().callback(interaction)


class ToggleButton(RoutedButton):
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


class IconButton(RoutedButton):
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
            label="\u200b",
            custom_id=custom_id,
            style=style,
            emoji=emoji,
            row=row
        )
        if tooltip:
            self.button_type._underlying.set_tooltip(tooltip)


class BackButton(RoutedButton):
    """Back navigation button."""

    def __init__(self, row: int = 4):
        super().__init__(
            label=i18n.get("buttons.back"),
            custom_id="nav_back",
            style=discord.ButtonStyle.secondary,
            emoji="🔙",
            row=row
        )


class HomeButton(RoutedButton):
    """Home navigation button."""

    def __init__(self, row: int = 4):
        super().__init__(
            label=i18n.get("buttons.home"),
            custom_id="nav_home",
            style=discord.ButtonStyle.primary,
            emoji="🏠",
            row=row
        )


class CloseButton(RoutedButton):
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
        """Close button: delete message then route to dispatcher."""
        if interaction.message:
            try:
                await interaction.message.delete()
            except discord.NotFound:
                pass
        await super().callback(interaction)


class NavigationButtonGroup(ui.View):
    """Navigation button group with back and home buttons."""

    def __init__(self, show_close: bool = False, row: int = 4):
        super().__init__(timeout=300)

        self.add_item(BackButton(row=row))
        self.add_item(HomeButton(row=row))

        if show_close:
            self.add_item(CloseButton(row=row))


class SelectOptionButton(RoutedButton):
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


class ActionRowButton(RoutedButton):
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
