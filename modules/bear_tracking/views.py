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
    """Main bear tracking callback."""
    view = BearTrackingView(bot, interaction.user.id)
    embed = view.create_embed()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def bear_add_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Add bear hunt callback."""
    embed = discord.Embed(
        title="🐻 إضافة صيد دب جديد",
        description="الرجاء إدخال بيانات الصيد:\n\n📝 الاسم:\n💰 التعويض:\n📅 التاريخ:",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def bear_damage_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Bear damage record callback."""
    embed = discord.Embed(
        title="📝 تسجيل أضرار الدب",
        description="سجل الأضرار فارغ حالياً.",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def bear_leaderboard_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Bear leaderboard callback."""
    embed = discord.Embed(
        title="🏆 قائمة المتصدرين",
        description="لا توجد بيانات بعد.",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def bear_report_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Bear report callback."""
    embed = discord.Embed(
        title="📊 تقرير الدببة",
        description="لا توجد بيانات بعد.",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def bear_ocr_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Bear OCR import callback."""
    embed = discord.Embed(
        title="📷 استيراد عبر OCR",
        description="أرسل صورة لالتقاط بيانات الدببة تلقائياً.",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def bear_archive_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Bear archive callback."""
    embed = discord.Embed(
        title="📦 أرشيف النتائج",
        description="لا توجد نتائج محفوظة.",
        color=0x8B4513
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)
