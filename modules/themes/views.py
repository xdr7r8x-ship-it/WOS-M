"""
WOS-M Themes Module
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
from views.buttons import ActionButton

class ThemesView(BaseView):
    """Themes and branding management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("themes.title"),
                description="",
                icon="🎨",
                color=0xe91e63
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        self.add_item(ActionButton(
            label=i18n.get("themes.bot_name"),
            custom_id="theme_bot_name",
            style=discord.ButtonStyle.primary,
            emoji="🤖",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("themes.primary_color"),
            custom_id="theme_primary_color",
            style=discord.ButtonStyle.primary,
            emoji="🎨",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("themes.preview"),
            custom_id="theme_preview",
            style=discord.ButtonStyle.secondary,
            emoji="👁️",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("themes.footer_text"),
            custom_id="theme_footer",
            style=discord.ButtonStyle.secondary,
            emoji="📝",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("themes.signature"),
            custom_id="theme_signature",
            style=discord.ButtonStyle.secondary,
            emoji="✍️",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("themes.reset_theme"),
            custom_id="theme_reset",
            style=discord.ButtonStyle.danger,
            emoji="🔄",
            row=1
        ))

async def themes_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for themes."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    view = ThemesView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_themes",
        category=AuditCategory.THEMES
    )

async def theme_bot_name_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_bot_name - Change bot display name."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class ThemeBotNameModal(ui.Modal, title="تغيير اسم البوت"):
        name_input = ui.TextInput(
            label="اسم البوت الجديد",
            placeholder="مثال: WOS-M",
            required=True,
            min_length=1,
            max_length=32
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                new_name = self.name_input.value.strip()
                
                # Save to database
                await db.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES ('theme_bot_name', ?, datetime('now'))
                """, (new_name,))
                
                await interaction.response.send_message(
                    f"✅ تم تغيير اسم البوت إلى `{new_name}`",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="change_theme_bot_name",
                    category=AuditCategory.THEMES,
                    details={"name": new_name}
                )
                
            except Exception:
                import logging
                logging.exception("theme_bot_name failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تغيير اسم البوت",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("theme_bot_name modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(ThemeBotNameModal())


async def theme_primary_color_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_primary_color - Change primary color."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class ThemeColorModal(ui.Modal, title="تغيير اللون الأساسي"):
        color_input = ui.TextInput(
            label="اللون (Hex)",
            placeholder="مثال: #3498db",
            required=True,
            min_length=7,
            max_length=7
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                color_hex = self.color_input.value.strip()
                
                # Validate hex color
                if not color_hex.startswith('#') or len(color_hex) != 7:
                    await interaction.response.send_message(
                        "❌ يجب إدخال لون Hex صحيح (مثال: #3498db)",
                        ephemeral=True
                    )
                    return
                
                try:
                    int(color_hex[1:], 16)
                except ValueError:
                    await interaction.response.send_message(
                        "❌ اللون Hex غير صالح",
                        ephemeral=True
                    )
                    return
                
                # Save to database
                await db.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES ('theme_primary_color', ?, datetime('now'))
                """, (color_hex,))
                
                await interaction.response.send_message(
                    f"✅ تم تغيير اللون الأساسي إلى `{color_hex}`",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="change_theme_color",
                    category=AuditCategory.THEMES,
                    details={"color": color_hex}
                )
                
            except Exception:
                import logging
                logging.exception("theme_primary_color failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تغيير اللون",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("theme_primary_color modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(ThemeColorModal())


async def theme_footer_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_footer - Change footer text."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class ThemeFooterModal(ui.Modal, title="تغيير نص التذييل"):
        footer_input = ui.TextInput(
            label="نص التذييل",
            placeholder="مثال: WOS-M © 2024",
            required=True,
            min_length=1,
            max_length=200
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                footer_text = self.footer_input.value.strip()
                
                # Save to database
                await db.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES ('theme_footer_text', ?, datetime('now'))
                """, (footer_text,))
                
                await interaction.response.send_message(
                    f"✅ تم تغيير نص التذييل",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="change_theme_footer",
                    category=AuditCategory.THEMES
                )
                
            except Exception:
                import logging
                logging.exception("theme_footer failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تغيير نص التذييل",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("theme_footer modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(ThemeFooterModal())


async def theme_signature_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_signature - Change signature text."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class ThemeSignatureModal(ui.Modal, title="تغيير التوقيع"):
        signature_input = ui.TextInput(
            label="نص التوقيع",
            placeholder="مثال: Made with ❤️ by WOS Team",
            required=True,
            min_length=1,
            max_length=200
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                signature_text = self.signature_input.value.strip()
                
                # Save to database
                await db.execute("""
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES ('theme_signature', ?, datetime('now'))
                """, (signature_text,))
                
                await interaction.response.send_message(
                    f"✅ تم تغيير التوقيع",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="change_theme_signature",
                    category=AuditCategory.THEMES
                )
                
            except Exception:
                import logging
                logging.exception("theme_signature failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تغيير التوقيع",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("theme_signature modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(ThemeSignatureModal())


async def theme_preview_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_preview - Preview current theme."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    await interaction.response.send_message("⏳ جاري تحميل معاينة السمة...", ephemeral=True)
    
    try:
        # Get current theme settings
        settings = await db.fetchall("""
            SELECT key, value FROM bot_settings 
            WHERE key LIKE 'theme_%'
        """)
        
        theme_data = {s.get('key'): s.get('value') for s in settings}
        
        # Get default theme values
        bot_name = theme_data.get('theme_bot_name', bot.user.name if hasattr(bot, 'user') else 'WOS-M')
        primary_color = theme_data.get('theme_primary_color', '#3498db')
        footer_text = theme_data.get('theme_footer_text', 'WOS-M • Theme Preview')
        
        # Parse color for embed
        try:
            color_int = int(primary_color[1:], 16)
        except:
            color_int = 0x3498db
        
        embed = discord.Embed(
            title=f"🎨 معاينة السمة: {bot_name}",
            description="هذه معاينة للسمات الحالية",
            color=color_int
        )
        
        embed.add_field(name="اسم البوت", value=bot_name, inline=True)
        embed.add_field(name="اللون الأساسي", value=primary_color, inline=True)
        embed.add_field(name="التذييل", value=footer_text, inline=False)
        
        if theme_data.get('theme_signature'):
            embed.add_field(name="التوقيع", value=theme_data.get('theme_signature'), inline=False)
        
        embed.set_footer(text=footer_text)
        
        await interaction.edit_original_response(embed=embed)
        
    except Exception:
        import logging
        logging.exception("theme_preview failed")
        await interaction.edit_original_response(
            content="❌ حدث خطأ أثناء تحميل معاينة السمة"
        )


async def theme_reset_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for theme_reset - Reset theme to defaults."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class ResetConfirmModal(ui.Modal, title="تأكيد إعادة تعيين السمة"):
        confirm_input = ui.TextInput(
            label="اكتب 'تأكيد' لإعادة تعيين السمة",
            placeholder="تأكيد",
            required=True,
            min_length=4,
            max_length=10
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            if self.confirm_input.value.strip() != "تأكيد":
                await interaction.response.send_message(
                    "❌ يجب كتابة 'تأكيد' لإعادة تعيين السمة",
                    ephemeral=True
                )
                return
            
            try:
                # Reset theme settings
                await db.execute("""
                    DELETE FROM bot_settings WHERE key LIKE 'theme_%'
                """)
                
                await interaction.response.send_message(
                    "✅ تم إعادة تعيين جميع إعدادات السمة إلى الإعدادات الافتراضية",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="reset_theme",
                    category=AuditCategory.THEMES
                )
                
            except Exception:
                import logging
                logging.exception("theme_reset failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء إعادة تعيين السمة",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("theme_reset modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(ResetConfirmModal())
