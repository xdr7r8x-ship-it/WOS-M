"""
WOS-M Gift Codes Views
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
from views.modals import GiftCodeModal
from modules.gift_codes.panel import GiftCodesPanelView, BatchRedeemView
from modules.gift_codes.service import gift_code_service
from modules.gift_codes.redemption_engine import redemption_engine
from modules.gift_codes.batch_runner import batch_runner


class GiftCodesView(BaseView):
    """Gift codes main view."""
    
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
        """Add management buttons."""
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.add_code"),
            custom_id="gift_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("gift_codes.redeem_title"),
            custom_id="gift_redeem_single",
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
            row=1
        ))


async def gift_codes_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for gift codes."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(
            i18n.get("messages.no_permission"),
            ephemeral=True
        )
        return
    
    view = GiftCodesView(bot, interaction.user.id)
    
    # Add stats to description
    stats = await gift_code_service.get_stats()
    description = f"**{i18n.get('gift_codes.status')}:**\n"
    description += f"- {i18n.get('gift_codes.status_pending')}: {stats.get('pending', 0)}\n"
    description += f"- {i18n.get('gift_codes.status_valid')}: {stats.get('valid', 0)}\n"
    description += f"- {i18n.get('gift_codes.status_redeemed')}: {stats.get('redeemed', 0)}\n"
    description += f"- {i18n.get('gift_codes.status_failed')}: {stats.get('failed', 0)}"
    
    embed = view.create_embed(description=description)
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_gift_codes",
        category=AuditCategory.GIFT_CODES
    )


async def add_gift_code_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for adding a gift code."""
    modal = GiftCodeModal(mode="add")
    await interaction.response.send_modal(modal)
    
    await modal.wait()
    
    code = modal.code_input.value.strip().upper()
    
    if not code:
        await interaction.followup.send(
            i18n.get("messages.required_field"),
            ephemeral=True
        )
        return
    
    try:
        code_id = await gift_code_service.add_code(
            code=code,
            added_by=str(interaction.user.id)
        )
        
        await interaction.followup.send(
            f"✅ {i18n.get('messages.success')}\n{i18n.get('gift_codes.code')}: `{code}`",
            ephemeral=True
        )
        
        await audit_log.log(
            user_id=str(interaction.user.id),
            user_name=str(interaction.user),
            action="add_gift_code",
            category=AuditCategory.GIFT_CODES,
            details={"code": code, "code_id": code_id}
        )
        
    except Exception as e:
        await interaction.followup.send(
            f"❌ {i18n.get('messages.error')}: {str(e)}",
            ephemeral=True
        )


async def redeem_single_code_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for single code redemption."""
    # Show a modal to get code and FID
    modal = GiftCodeModal(mode="redeem")
    await interaction.response.send_modal(modal)
    
    await modal.wait()
    
    code = modal.code_input.value.strip().upper()
    
    # Get player FID
    await interaction.followup.send(
        "📝 " + i18n.get("players.fid"),
        ephemeral=True
    )


async def batch_redeem_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for batch redemption."""
    view = BatchRedeemView(bot, interaction.user.id)
    embed = view.create_embed(
        description="📦 " + i18n.get("gift_codes.batch_redeem")
    )
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def auto_redeem_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for auto redeem."""
    await interaction.response.send_message(
        f"🤖 {i18n.get('gift_codes.auto_redeem')}\n" +
        i18n.get("messages.select_option"),
        ephemeral=True
    )


async def gift_report_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for gift codes report."""
    stats = await gift_code_service.get_stats()
    
    embed = discord.Embed(
        title=f"📋 {i18n.get('gift_codes.report')}",
        color=0x3498db
    )
    
    embed.add_field(
        name=i18n.get("gift_codes.title"),
        value=f"**{i18n.get('gift_codes.status_pending')}:** {stats.get('pending', 0)}\n"
              f"**{i18n.get('gift_codes.status_valid')}:** {stats.get('valid', 0)}\n"
              f"**{i18n.get('gift_codes.status_redeemed')}:** {stats.get('redeemed', 0)}\n"
              f"**{i18n.get('gift_codes.status_failed')}:** {stats.get('failed', 0)}",
        inline=True
    )
    
    embed.set_footer(text=i18n.get("bot.footer"))
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def gift_settings_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for gift codes settings."""
    embed = discord.Embed(
        title=f"⚙️ {i18n.get('gift_codes.code_settings')}",
        color=0x3498db
    )
    
    embed.add_field(
        name=i18n.get("gift_codes.captcha_settings"),
        value="🔐 Captcha Service: Not configured",
        inline=False
    )
    
    embed.set_footer(text=i18n.get("bot.footer"))
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
