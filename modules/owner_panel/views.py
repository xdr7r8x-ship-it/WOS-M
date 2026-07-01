"""
WOS-M Owner Panel Module
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
from views.buttons import ActionButton, BackButton, HomeButton
from views.selects import LanguageSelect, OwnerPanelSectionSelect, FeatureSelect


class OwnerPanelView(BaseView):
    """Owner panel main view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.title"),
                description=i18n.get("owner_panel.welcome"),
                icon="👑",
                color=0xe74c3c
            )
        )
        
        self.add_item(OwnerPanelSectionSelect())
        self.add_back_home_buttons()


class LanguageManagementView(BaseView):
    """Language management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.language_management"),
                description="",
                icon="🌐",
                color=0x1abc9c
            )
        )
        
        self.add_item(LanguageSelect(i18n.current_locale))
        self.add_back_home_buttons()


class ButtonManagementView(BaseView):
    """Button management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.button_management"),
                description="",
                icon="🔘",
                color=0x3498db
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.add_button"),
            custom_id="btn_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_button_name"),
            custom_id="btn_edit_name",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_button_icon"),
            custom_id="btn_edit_icon",
            style=discord.ButtonStyle.primary,
            emoji="🔣",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_button_order"),
            custom_id="btn_edit_order",
            style=discord.ButtonStyle.primary,
            emoji="📊",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.enable_button"),
            custom_id="btn_enable",
            style=discord.ButtonStyle.success,
            emoji="✅",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.disable_button"),
            custom_id="btn_disable",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            row=1
        ))


class TextManagementView(BaseView):
    """Text management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.text_management"),
                description="",
                icon="📝",
                color=0xf39c12
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_title"),
            custom_id="text_edit_title",
            style=discord.ButtonStyle.primary,
            emoji="📌",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_description"),
            custom_id="text_edit_desc",
            style=discord.ButtonStyle.primary,
            emoji="📄",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_messages"),
            custom_id="text_edit_msg",
            style=discord.ButtonStyle.primary,
            emoji="💬",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.reset_texts"),
            custom_id="text_reset",
            style=discord.ButtonStyle.danger,
            emoji="🔄",
            row=1
        ))


class IconManagementView(BaseView):
    """Icon management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.icon_management"),
                description="",
                icon="🎨",
                color=0x9b59b6
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_section_icon"),
            custom_id="icon_section",
            style=discord.ButtonStyle.primary,
            emoji="📁",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_button_icon_manage"),
            custom_id="icon_button",
            style=discord.ButtonStyle.primary,
            emoji="🔘",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_status_icon"),
            custom_id="icon_status",
            style=discord.ButtonStyle.primary,
            emoji="📊",
            row=0
        ))


class BrandingManagementView(BaseView):
    """Branding management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.branding_management"),
                description="",
                icon="🎨",
                color=0xe91e63
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.change_bot_name"),
            custom_id="brand_name",
            style=discord.ButtonStyle.primary,
            emoji="🤖",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.change_colors"),
            custom_id="brand_colors",
            style=discord.ButtonStyle.primary,
            emoji="🎨",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.save_theme"),
            custom_id="brand_save",
            style=discord.ButtonStyle.success,
            emoji="💾",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.reset_theme"),
            custom_id="brand_reset",
            style=discord.ButtonStyle.danger,
            emoji="🔄",
            row=1
        ))


class FeatureManagementView(BaseView):
    """Feature management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("owner_panel.feature_management"),
                description="",
                icon="⚙️",
                color=0x34495e
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.add_feature"),
            custom_id="feat_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.edit_feature"),
            custom_id="feat_edit",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.enable_feature"),
            custom_id="feat_enable",
            style=discord.ButtonStyle.success,
            emoji="✅",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.disable_feature"),
            custom_id="feat_disable",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.link_feature"),
            custom_id="feat_link",
            style=discord.ButtonStyle.primary,
            emoji="🔗",
            row=2
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("owner_panel.feature_registry"),
            custom_id="feat_registry",
            style=discord.ButtonStyle.secondary,
            emoji="📦",
            row=2
        ))


# Callbacks
async def owner_panel_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for owner panel."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = OwnerPanelView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_owner_panel",
        category=AuditCategory.OWNER_PANEL
    )


async def language_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for language management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = LanguageManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def button_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for button management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = ButtonManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def text_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for text management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = TextManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def icon_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for icon management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = IconManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def branding_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for branding management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = BrandingManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def feature_management_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for feature management."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.OWNER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = FeatureManagementView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# =============================================================================
# Callback stubs for dynamic routing
# Called by bot.py's _route_to_module
# =============================================================================

async def brand_colors_callback(bot, interaction):
    """Handle brand_colors button."""
    # TODO: Implement brand_colors functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def brand_name_callback(bot, interaction):
    """Handle brand_name button."""
    # TODO: Implement brand_name functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def brand_reset_callback(bot, interaction):
    """Handle brand_reset button."""
    # TODO: Implement brand_reset functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def brand_save_callback(bot, interaction):
    """Handle brand_save button."""
    # TODO: Implement brand_save functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_add_callback(bot, interaction):
    """Handle btn_add button."""
    # TODO: Implement btn_add functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_disable_callback(bot, interaction):
    """Handle btn_disable button."""
    # TODO: Implement btn_disable functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_edit_icon_callback(bot, interaction):
    """Handle btn_edit_icon button."""
    # TODO: Implement btn_edit_icon functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_edit_name_callback(bot, interaction):
    """Handle btn_edit_name button."""
    # TODO: Implement btn_edit_name functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_edit_order_callback(bot, interaction):
    """Handle btn_edit_order button."""
    # TODO: Implement btn_edit_order functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def btn_enable_callback(bot, interaction):
    """Handle btn_enable button."""
    # TODO: Implement btn_enable functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_add_callback(bot, interaction):
    """Handle feat_add button."""
    # TODO: Implement feat_add functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_disable_callback(bot, interaction):
    """Handle feat_disable button."""
    # TODO: Implement feat_disable functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_edit_callback(bot, interaction):
    """Handle feat_edit button."""
    # TODO: Implement feat_edit functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_enable_callback(bot, interaction):
    """Handle feat_enable button."""
    # TODO: Implement feat_enable functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_link_callback(bot, interaction):
    """Handle feat_link button."""
    # TODO: Implement feat_link functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def feat_registry_callback(bot, interaction):
    """Handle feat_registry button."""
    # TODO: Implement feat_registry functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def icon_button_callback(bot, interaction):
    """Handle icon_button button."""
    # TODO: Implement icon_button functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def icon_section_callback(bot, interaction):
    """Handle icon_section button."""
    # TODO: Implement icon_section functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def icon_status_callback(bot, interaction):
    """Handle icon_status button."""
    # TODO: Implement icon_status functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def text_edit_desc_callback(bot, interaction):
    """Handle text_edit_desc button."""
    # TODO: Implement text_edit_desc functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def text_edit_msg_callback(bot, interaction):
    """Handle text_edit_msg button."""
    # TODO: Implement text_edit_msg functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def text_edit_title_callback(bot, interaction):
    """Handle text_edit_title button."""
    # TODO: Implement text_edit_title functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

async def text_reset_callback(bot, interaction):
    """Handle text_reset button."""
    # TODO: Implement text_reset functionality
    await interaction.response.send_message(
        "⚠️ هذه الميزة قيد التطوير.",
        ephemeral=True
    )

