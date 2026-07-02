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
            items=[],
            items_per_page=10,
            page_info=PageInfo(
                title=i18n.get("alliances.title"),
                icon="🏰",
                color=0x3498db
            )
        )
    
    async def load_alliances(self):
        """Load alliances from database."""
        rows = await db.fetchall("SELECT * FROM alliances ORDER BY name")
        self.items = [dict(row) for row in rows]
        self._total_pages = max(1, (len(self.items) + self.items_per_page - 1) // self.items_per_page)
        self._update_buttons()


async def alliances_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for alliances."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية عرض التحالفات.",
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


async def alliance_add_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_add button - Add a new alliance."""
    guard = PermissionGuard(bot)

    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ADMIN):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية إضافة تحالفات.",
            ephemeral=True
        )
        return

    modal = AllianceAddModal(bot)
    await interaction.response.send_modal(modal)


class AllianceAddModal(ui.Modal):
    """Modal for adding a new alliance."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="➕ إضافة تحالف جديد")
        self.bot = bot

        self.name_input = ui.TextInput(
            label="اسم التحالف",
            placeholder="اسم التحالف",
            required=True,
            min_length=1,
            max_length=100
        )

        self.state_kid_input = ui.TextInput(
            label="State KID / Alliance ID",
            placeholder="12345678",
            required=True,
            min_length=1,
            max_length=50
        )

        self.discord_role_input = ui.TextInput(
            label="Discord Role ID (اختياري)",
            placeholder="اتركه فارغاً",
            required=False
        )

        self.add_item(self.name_input)
        self.add_item(self.state_kid_input)
        self.add_item(self.discord_role_input)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_input.value.strip()
        state_kid = self.state_kid_input.value.strip()
        discord_role = self.discord_role_input.value.strip() if self.discord_role_input.value else None

        try:
            existing = await db.fetchone(
                "SELECT id FROM alliances WHERE name = ? OR state_kid = ?",
                (name, state_kid)
            )
            if existing:
                await interaction.response.send_message(
                    "❌ التحالف موجود بالفعل.",
                    ephemeral=True
                )
                return

            cursor = await db.execute(
                """INSERT INTO alliances (name, state_kid, discord_role_id, is_active)
                   VALUES (?, ?, ?, 1)""",
                (name, state_kid, discord_role)
            )
            await db.commit()
            alliance_id = cursor.lastrowid

            embed = discord.Embed(title="✅ تم إضافة التحالف", color=0x2ecc71)
            embed.add_field(name="الاسم", value=name, inline=True)
            embed.add_field(name="State KID", value=state_kid, inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

            await audit_log.log(
                user_id=str(interaction.user.id),
                user_name=str(interaction.user),
                action="add_alliance",
                category=AuditCategory.ALLIANCES,
                details={"name": name, "state_kid": state_kid, "alliance_id": alliance_id}
            )

        except Exception:
            import logging
            logging.exception("AllianceAddModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء إضافة التحالف. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceAddModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "حدث خطأ أثناء حفظ التحالف.",
                ephemeral=True
            )


async def alliance_list_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_list button - List all alliances."""
    guard = PermissionGuard(bot)
    
    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.MEMBER):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية عرض التحالفات.",
            ephemeral=True
        )
        return
    
    try:
        rows = await db.fetchall("SELECT * FROM alliances ORDER BY name LIMIT 100")
        
        if not rows:
            await interaction.response.send_message(
                "🏰 لا يوجد تحالفات مسجلة.",
                ephemeral=True
            )
            return
        
        view = AllianceListView(bot, interaction.user.id)
        view.items = [dict(row) for row in rows]
        view._total_pages = max(1, (len(view.items) + view.items_per_page - 1) // view.items_per_page)
        view._update_buttons()
        
        embed = view.create_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    except Exception:
        await interaction.response.send_message(
            "❌ حدث خطأ أثناء تحميل التحالفات. تم تسجيل التفاصيل.",
            ephemeral=True
        )


async def alliance_edit_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_edit button - Edit an alliance."""
    guard = PermissionGuard(bot)

    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ADMIN):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية تعديل التحالفات.",
            ephemeral=True
        )
        return

    modal = AllianceEditModal(bot)
    await interaction.response.send_modal(modal)


class AllianceEditModal(ui.Modal):
    """Modal for editing an alliance."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="✏️ تعديل التحالف")
        self.bot = bot

        self.alliance_id_input = ui.TextInput(
            label="ID التحالف",
            placeholder="1",
            required=True
        )

        self.name_input = ui.TextInput(
            label="اسم التحالف الجديد",
            placeholder="اتركه فارغاً لعدم التغيير",
            required=False
        )

        self.state_kid_input = ui.TextInput(
            label="State KID الجديد",
            placeholder="اتركه فارغاً لعدم التغيير",
            required=False
        )

        self.add_item(self.alliance_id_input)
        self.add_item(self.name_input)
        self.add_item(self.state_kid_input)

    async def on_submit(self, interaction: discord.Interaction):
        alliance_id = self.alliance_id_input.value.strip()

        try:
            alliance = await db.fetchone("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
            if not alliance:
                await interaction.response.send_message(
                    f"❌ التحالف `{alliance_id}` غير موجود.",
                    ephemeral=True
                )
                return

            updates = []
            params = []

            if self.name_input.value:
                updates.append("name = ?")
                params.append(self.name_input.value.strip())

            if self.state_kid_input.value:
                updates.append("state_kid = ?")
                params.append(self.state_kid_input.value.strip())

            if not updates:
                await interaction.response.send_message(
                    "❌ لم يتم إدخال أي بيانات للتعديل.",
                    ephemeral=True
                )
                return

            params.append(alliance_id)

            await db.execute(
                f"UPDATE alliances SET {', '.join(updates)} WHERE id = ?",
                tuple(params)
            )
            await db.commit()

            embed = discord.Embed(title="✅ تم تعديل التحالف", color=0x2ecc71)
            embed.add_field(name="ID", value=alliance_id, inline=True)
            embed.add_field(name="الاسم الجديد", value=self.name_input.value or alliance["name"], inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

            await audit_log.log(
                user_id=str(interaction.user.id),
                user_name=str(interaction.user),
                action="edit_alliance",
                category=AuditCategory.ALLIANCES,
                details={"alliance_id": alliance_id}
            )

        except Exception:
            import logging
            logging.exception("AllianceEditModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء تعديل التحالف. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceEditModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "حدث خطأ أثناء تعديل التحالف.",
                ephemeral=True
            )


async def alliance_delete_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_delete button - Delete an alliance."""
    guard = PermissionGuard(bot)

    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ADMIN):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية حذف التحالفات.",
            ephemeral=True
        )
        return

    modal = AllianceDeleteModal(bot)
    await interaction.response.send_modal(modal)


class AllianceDeleteModal(ui.Modal):
    """Modal for deleting an alliance."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="🗑️ حذف التحالف")
        self.bot = bot

        self.alliance_id_input = ui.TextInput(
            label="ID التحالف",
            placeholder="1",
            required=True
        )

        self.confirm_input = ui.TextInput(
            label="اكتب 'حذف' للتأكيد",
            placeholder="حذف",
            required=True
        )

        self.add_item(self.alliance_id_input)
        self.add_item(self.confirm_input)

    async def on_submit(self, interaction: discord.Interaction):
        alliance_id = self.alliance_id_input.value.strip()
        confirm = self.confirm_input.value.strip()

        if confirm != "حذف":
            await interaction.response.send_message(
                "❌ لم يتم تأكيد الحذف.",
                ephemeral=True
            )
            return

        try:
            alliance = await db.fetchone("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
            if not alliance:
                await interaction.response.send_message(
                    f"❌ التحالف `{alliance_id}` غير موجود.",
                    ephemeral=True
                )
                return

            await db.execute("DELETE FROM alliances WHERE id = ?", (alliance_id,))
            await db.commit()

            embed = discord.Embed(title="✅ تم حذف التحالف", color=0xe74c3c)
            embed.add_field(name="الاسم", value=alliance["name"], inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

            await audit_log.log(
                user_id=str(interaction.user.id),
                user_name=str(interaction.user),
                action="delete_alliance",
                category=AuditCategory.ALLIANCES,
                details={"alliance_id": alliance_id, "name": alliance["name"]}
            )

        except Exception:
            import logging
            logging.exception("AllianceDeleteModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء حذف التحالف. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceDeleteModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message("حدث خطأ.", ephemeral=True)


async def alliance_sync_settings_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_sync_settings button."""
    guard = PermissionGuard(bot)

    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ADMIN):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية تعديل الإعدادات.",
            ephemeral=True
        )
        return

    modal = AllianceSyncModal(bot)
    await interaction.response.send_modal(modal)


class AllianceSyncModal(ui.Modal):
    """Modal for syncing alliance settings."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="🔄 مزامنة إعدادات التحالف")
        self.bot = bot

        self.alliance_id_input = ui.TextInput(
            label="ID التحالف",
            placeholder="1",
            required=True
        )

        self.discord_role_input = ui.TextInput(
            label="Discord Role ID",
            placeholder="اتركه فارغاً لعدم التغيير",
            required=False
        )

        self.add_item(self.alliance_id_input)
        self.add_item(self.discord_role_input)

    async def on_submit(self, interaction: discord.Interaction):
        alliance_id = self.alliance_id_input.value.strip()

        try:
            alliance = await db.fetchone("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
            if not alliance:
                await interaction.response.send_message(
                    f"❌ التحالف `{alliance_id}` غير موجود.",
                    ephemeral=True
                )
                return

            updates = ["updated_at = CURRENT_TIMESTAMP"]
            params = []

            if self.discord_role_input.value:
                updates.append("discord_role_id = ?")
                params.append(self.discord_role_input.value.strip())

            params.append(alliance_id)

            await db.execute(
                f"UPDATE alliances SET {', '.join(updates)} WHERE id = ?",
                tuple(params)
            )
            await db.commit()

            embed = discord.Embed(title="✅ تم مزامنة الإعدادات", color=0x2ecc71)
            embed.add_field(name="التحالف", value=alliance["name"], inline=True)

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception:
            import logging
            logging.exception("AllianceSyncModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء المزامنة. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceSyncModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message("حدث خطأ.", ephemeral=True)


async def alliance_gift_settings_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_gift_settings button."""
    guard = PermissionGuard(bot)

    if not await guard.has_permission(str(interaction.user.id), PermissionLevel.ADMIN):
        await interaction.response.send_message(
            "❌ ليس لديك صلاحية تعديل إعدادات الهدايا.",
            ephemeral=True
        )
        return

    modal = AllianceGiftSettingsModal(bot)
    await interaction.response.send_modal(modal)


class AllianceGiftSettingsModal(ui.Modal):
    """Modal for alliance gift settings."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="🎁 إعدادات استرداد الهدايا")
        self.bot = bot

        self.alliance_id_input = ui.TextInput(
            label="ID التحالف",
            placeholder="1",
            required=True
        )

        self.auto_redeem_input = ui.TextInput(
            label="الاسترداد التلقائي",
            placeholder="اكتب 'تفعيل' أو 'إلغاء'",
            required=True
        )

        self.add_item(self.alliance_id_input)
        self.add_item(self.auto_redeem_input)

    async def on_submit(self, interaction: discord.Interaction):
        alliance_id = self.alliance_id_input.value.strip()
        action = self.auto_redeem_input.value.strip()

        try:
            alliance = await db.fetchone("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
            if not alliance:
                await interaction.response.send_message(
                    f"❌ التحالف `{alliance_id}` غير موجود.",
                    ephemeral=True
                )
                return

            enabled = 1 if action == "تفعيل" else 0

            await db.execute(
                "UPDATE alliances SET auto_gift_enabled = ? WHERE id = ?",
                (enabled, alliance_id)
            )
            await db.commit()

            status = "✅ مفعّل" if enabled else "❌ معطّل"

            embed = discord.Embed(
                title=f"🎁 {status}",
                description=f"**التحالف:** {alliance['name']}",
                color=0x2ecc71 if enabled else 0xe74c3c
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

            await audit_log.log(
                user_id=str(interaction.user.id),
                user_name=str(interaction.user),
                action="update_gift_settings",
                category=AuditCategory.GIFT_CODES,
                details={"alliance_id": alliance_id, "auto_gift_enabled": enabled}
            )

        except Exception:
            import logging
            logging.exception("AllianceGiftSettingsModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء تحديث الإعدادات. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceGiftSettingsModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message("حدث خطأ.", ephemeral=True)


async def alliance_redeem_modal_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_redeem_modal button."""
    modal = AllianceRedeemModal(bot)
    await interaction.response.send_modal(modal)


class AllianceRedeemModal(ui.Modal):
    """Modal for redeeming gift codes for alliance."""

    def __init__(self, bot: WOSMBot):
        super().__init__(title="🎁 استرداد هدايا للتحالف")
        self.bot = bot

        self.alliance_id_input = ui.TextInput(
            label="ID التحالف",
            placeholder="1",
            required=True
        )

        self.code_input = ui.TextInput(
            label="كود الهدية",
            placeholder="WOSM123456",
            required=True
        )

        self.add_item(self.alliance_id_input)
        self.add_item(self.code_input)

    async def on_submit(self, interaction: discord.Interaction):
        alliance_id = self.alliance_id_input.value.strip()
        code = self.code_input.value.strip()

        try:
            alliance = await db.fetchone("SELECT * FROM alliances WHERE id = ?", (alliance_id,))
            if not alliance:
                await interaction.response.send_message(
                    f"❌ التحالف `{alliance_id}` غير موجود.",
                    ephemeral=True
                )
                return

            # Call redemption logic
            from modules.gift_codes.logic import redeem_gift_code
            success, msg = await redeem_gift_code(code, alliance_id)
            
            if success:
                await interaction.response.send_message(
                    f"✅ تم استرداد الكود `{code}` بنجاح!",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ فشل استرداد الكود: {msg}",
                    ephemeral=True
                )

        except Exception:
            import logging
            logging.exception("AllianceRedeemModal failed")
            await interaction.response.send_message(
                "❌ حدث خطأ أثناء استرداد الكود. تم تسجيل التفاصيل.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        import logging
        logging.exception("AllianceRedeemModal error", exc_info=error)
        if not interaction.response.is_done():
            await interaction.response.send_message("حدث خطأ.", ephemeral=True)


async def alliance_select_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Handle alliance_select from select menu."""
    if interaction.data.get("values"):
        selected_id = interaction.data["values"][0]
        await interaction.response.send_message(
            f"✅ تم اختيار التحالف: `{selected_id}`",
            ephemeral=True
        )