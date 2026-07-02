"""
WOS-M Notifications Module
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

class NotificationsView(BaseView):
    """Notifications management view."""
    
    def __init__(self, bot: WOSMBot, user_id: int):
        self.bot = bot
        super().__init__(
            user_id=user_id,
            page_info=PageInfo(
                title=i18n.get("notifications.title"),
                description="",
                icon="🔔",
                color=0xf39c12
            )
        )
        
        self._add_buttons()
        self.add_back_home_buttons()
    
    def _add_buttons(self):
        self.add_item(ActionButton(
            label=i18n.get("notifications.add_notification"),
            custom_id="notif_add",
            style=discord.ButtonStyle.success,
            emoji="➕",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.view"),
            custom_id="notif_list",
            style=discord.ButtonStyle.primary,
            emoji="📋",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.edit"),
            custom_id="notif_edit",
            style=discord.ButtonStyle.primary,
            emoji="✏️",
            row=0
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.delete"),
            custom_id="notif_delete",
            style=discord.ButtonStyle.danger,
            emoji="🗑️",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.enable"),
            custom_id="notif_enable",
            style=discord.ButtonStyle.success,
            emoji="✅",
            row=1
        ))
        
        self.add_item(ActionButton(
            label=i18n.get("buttons.disable"),
            custom_id="notif_disable",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            row=1
        ))

async def notifications_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notifications."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    view = NotificationsView(bot, interaction.user.id)
    embed = view.create_embed()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await audit_log.log(
        user_id=str(interaction.user.id),
        user_name=str(interaction.user),
        action="view_notifications",
        category=AuditCategory.NOTIFICATIONS
    )

async def notif_add_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_add - Create a new notification."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ALLIANCE_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class AddNotifModal(ui.Modal, title="إضافة إشعار جديد"):
        title_input = ui.TextInput(
            label="عنوان الإشعار",
            placeholder="مثال: تحديث جديد",
            required=True,
            min_length=1,
            max_length=100
        )
        content_input = ui.TextInput(
            label="محتوى الإشعار",
            placeholder="اكتب محتوى الإشعار هنا...",
            style=discord.TextStyle.paragraph,
            required=True,
            min_length=1,
            max_length=1000
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                title = self.title_input.value.strip()
                content = self.content_input.value.strip()
                
                # Save notification
                await db.execute("""
                    INSERT INTO notifications (title, content, created_by, created_at, enabled)
                    VALUES (?, ?, ?, datetime('now'), 1)
                """, (title, content, str(interaction.user.id)))
                
                await interaction.response.send_message(
                    f"✅ تم إضافة الإشعار بنجاح",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="add_notification",
                    category=AuditCategory.NOTIFICATIONS,
                    details={"title": title}
                )
                
            except Exception:
                import logging
                logging.exception("notif_add failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء إضافة الإشعار",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("notif_add modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(AddNotifModal())


async def notif_list_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_list - List all notifications."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    await interaction.response.send_message("⏳ جاري تحميل الإشعارات...", ephemeral=True)
    
    try:
        notifications = await db.fetchall("""
            SELECT id, title, content, enabled, created_at 
            FROM notifications 
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        embed = discord.Embed(
            title="📋 قائمة الإشعارات",
            color=0xf39c12
        )
        
        if not notifications:
            embed.description = "لا توجد إشعارات حالياً"
        else:
            for notif in notifications[:10]:
                status = "🟢 مفعل" if notif.get('enabled') else "🔴 معطل"
                embed.add_field(
                    name=f"{status} {notif.get('title', '—')[:50]}",
                    value=f"ID: `{notif.get('id')}` | {notif.get('created_at', '—')[:10]}",
                    inline=False
                )
        
        embed.set_footer(text=f"إجمالي: {len(notifications)} إشعار")
        
        await interaction.edit_original_response(embed=embed)
        
    except Exception:
        import logging
        logging.exception("notif_list failed")
        await interaction.edit_original_response(
            content="❌ حدث خطأ أثناء تحميل الإشعارات"
        )


async def notif_edit_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_edit - Edit a notification."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ALLIANCE_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class EditNotifModal(ui.Modal, title="تعديل إشعار"):
        notif_id_input = ui.TextInput(
            label="معرف الإشعار",
            placeholder="معرف الإشعار",
            required=True
        )
        title_input = ui.TextInput(
            label="العنوان الجديد",
            placeholder="اتركه فارغاً لعدم التغيير",
            required=False,
            min_length=1,
            max_length=100
        )
        content_input = ui.TextInput(
            label="المحتوى الجديد",
            placeholder="اتركه فارغاً لعدم التغيير",
            style=discord.TextStyle.paragraph,
            required=False,
            min_length=1,
            max_length=1000
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            try:
                notif_id = self.notif_id_input.value.strip()
                new_title = self.title_input.value.strip() or None
                new_content = self.content_input.value.strip() or None
                
                if not new_title and not new_content:
                    await interaction.response.send_message(
                        "❌ يجب إدخال عنوان أو محتوى جديد على الأقل",
                        ephemeral=True
                    )
                    return
                
                # Build update query
                updates = []
                values = []
                if new_title:
                    updates.append("title = ?")
                    values.append(new_title)
                if new_content:
                    updates.append("content = ?")
                    values.append(new_content)
                
                values.append(notif_id)
                
                await db.execute(
                    f"UPDATE notifications SET {', '.join(updates)} WHERE id = ?",
                    tuple(values)
                )
                
                await interaction.response.send_message(
                    f"✅ تم تعديل الإشعار رقم `{notif_id}`",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="edit_notification",
                    category=AuditCategory.NOTIFICATIONS,
                    details={"id": notif_id}
                )
                
            except Exception:
                import logging
                logging.exception("notif_edit failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تعديل الإشعار",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("notif_edit modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(EditNotifModal())


async def notif_delete_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_delete - Delete a notification."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.GLOBAL_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    class DeleteNotifModal(ui.Modal, title="حذف إشعار"):
        notif_id_input = ui.TextInput(
            label="معرف الإشعار للحذف",
            placeholder="معرف الإشعار",
            required=True
        )
        confirm_input = ui.TextInput(
            label="اكتب 'حذف' للتأكيد",
            placeholder="حذف",
            required=True
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            if self.confirm_input.value.strip() != "حذف":
                await interaction.response.send_message(
                    "❌ يجب كتابة 'حذف' للتأكيد",
                    ephemeral=True
                )
                return
            
            try:
                notif_id = self.notif_id_input.value.strip()
                
                # Delete notification
                await db.execute("DELETE FROM notifications WHERE id = ?", (notif_id,))
                
                await interaction.response.send_message(
                    f"✅ تم حذف الإشعار رقم `{notif_id}`",
                    ephemeral=True
                )
                
                await audit_log.log(
                    user_id=str(interaction.user.id),
                    user_name=str(interaction.user),
                    action="delete_notification",
                    category=AuditCategory.NOTIFICATIONS,
                    details={"id": notif_id}
                )
                
            except Exception:
                import logging
                logging.exception("notif_delete failed")
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء حذف الإشعار",
                    ephemeral=True
                )
        
        async def on_error(self, interaction: discord.Interaction, error: Exception):
            import logging
            logging.exception("notif_delete modal error")
            try:
                await interaction.response.send_message(
                    f"❌ خطأ: {str(error)[:100]}",
                    ephemeral=True
                )
            except:
                pass
    
    await interaction.response.send_modal(DeleteNotifModal())


async def notif_enable_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_enable - Enable a notification."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ALLIANCE_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    await interaction.response.send_message("⏳ جاري تفعيل الإشعارات...", ephemeral=True)
    
    try:
        disabled = await db.fetchall("""
            SELECT id, title FROM notifications WHERE enabled = 0
        """)
        
        embed = discord.Embed(
            title="✅ تفعيل إشعار",
            description="الإشعارات المعطلة حالياً:",
            color=0x2ecc71
        )
        
        if not disabled:
            embed.description = "✅ لا توجد إشعارات معطلة"
        else:
            for notif in disabled[:10]:
                embed.add_field(
                    name=notif.get('title', '—')[:50],
                    value=f"ID: `{notif.get('id')}`",
                    inline=True
                )
        
        await interaction.edit_original_response(embed=embed)
        
        await audit_log.log(
            user_id=str(interaction.user.id),
            user_name=str(interaction.user),
            action="view_disabled_notifications",
            category=AuditCategory.NOTIFICATIONS
        )
        
    except Exception:
        import logging
        logging.exception("notif_enable failed")
        await interaction.edit_original_response(
            content="❌ حدث خطأ أثناء تفعيل الإشعارات"
        )


async def notif_disable_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for notif_disable - Disable a notification."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ALLIANCE_ADMIN):
        await interaction.response.send_message(i18n.get("messages.no_permission"), ephemeral=True)
        return
    
    await interaction.response.send_message("⏳ جاري تعطيل الإشعارات...", ephemeral=True)
    
    try:
        enabled = await db.fetchall("""
            SELECT id, title FROM notifications WHERE enabled = 1
        """)
        
        embed = discord.Embed(
            title="❌ تعطيل إشعار",
            description="الإشعارات المفعلة حالياً:",
            color=0xe74c3c
        )
        
        if not enabled:
            embed.description = "❌ لا توجد إشعارات مفعلة"
        else:
            for notif in enabled[:10]:
                embed.add_field(
                    name=notif.get('title', '—')[:50],
                    value=f"ID: `{notif.get('id')}`",
                    inline=True
                )
        
        await interaction.edit_original_response(embed=embed)
        
        await audit_log.log(
            user_id=str(interaction.user.id),
            user_name=str(interaction.user),
            action="view_enabled_notifications",
            category=AuditCategory.NOTIFICATIONS
        )
        
    except Exception:
        import logging
        logging.exception("notif_disable failed")
        await interaction.edit_original_response(
            content="❌ حدث خطأ أثناء تعطيل الإشعارات"
        )
