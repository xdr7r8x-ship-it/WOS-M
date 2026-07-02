"""
WOS-M Modal Views
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from discord import ui
from typing import Optional, Dict, Any

from core.i18n import i18n


class BaseModal(ui.Modal):
    """Base modal with common functionality."""
    
    def __init__(self, title: str, custom_id: str = ""):
        super().__init__(title=title, custom_id=custom_id, timeout=300)
        self.result: Optional[Dict[str, Any]] = None


class TextInputModal(BaseModal):
    """Modal with a single text input."""
    
    def __init__(
        self,
        title: str,
        label: str,
        placeholder: str = "",
        default_value: str = "",
        required: bool = True,
        max_length: int = 100
    ):
        super().__init__(title=title)
        
        self.text_input = ui.TextInput(
            label=label,
            placeholder=placeholder,
            default_value=default_value,
            required=required,
            max_length=max_length
        )
        self.add_item(self.text_input)


class AllianceModal(BaseModal):
    """Modal for alliance operations."""
    
    def __init__(self, mode: str = "add", alliance_data: Optional[Dict] = None):
        title = i18n.get("alliances.add_title") if mode == "add" else i18n.get("alliances.edit_title")
        super().__init__(title=title, custom_id=f"alliance_modal_{mode}")
        
        self.name_input = ui.TextInput(
            label=i18n.get("alliances.name"),
            placeholder="Enter alliance name",
            default_value=alliance_data.get("name", "") if alliance_data else "",
            required=True,
            max_length=100
        )
        
        self.state_kid_input = ui.TextInput(
            label=i18n.get("alliances.state_kid"),
            placeholder="Enter State/KID",
            default_value=alliance_data.get("state_kid", "") if alliance_data else "",
            required=False,
            max_length=50
        )
        
        self.discord_server_input = ui.TextInput(
            label=i18n.get("alliances.discord_server"),
            placeholder="Enter Discord server ID",
            default_value=alliance_data.get("discord_guild_id", "") if alliance_data else "",
            required=False,
            max_length=50
        )
        
        self.add_item(self.name_input)
        self.add_item(self.state_kid_input)
        self.add_item(self.discord_server_input)


class PlayerModal(BaseModal):
    """Modal for player operations."""
    
    def __init__(self, mode: str = "add", player_data: Optional[Dict] = None):
        title = i18n.get("players.add_title") if mode == "add" else i18n.get("players.edit_title")
        super().__init__(title=title, custom_id=f"player_modal_{mode}")
        
        self.fid_input = ui.TextInput(
            label=i18n.get("players.fid"),
            placeholder="Enter FID",
            default_value=player_data.get("fid", "") if player_data else "",
            required=True,
            max_length=50
        )
        
        self.name_input = ui.TextInput(
            label=i18n.get("players.player_name"),
            placeholder="Enter player name",
            default_value=player_data.get("name", "") if player_data else "",
            required=True,
            max_length=100
        )
        
        self.level_input = ui.TextInput(
            label=i18n.get("players.level"),
            placeholder="Enter player level",
            default_value=str(player_data.get("level", 1)) if player_data else "1",
            required=False,
            max_length=10
        )
        
        self.add_item(self.fid_input)
        self.add_item(self.name_input)
        self.add_item(self.level_input)


class GiftCodeModal(BaseModal):
    """Modal for gift code operations."""
    
    def __init__(self, mode: str = "add"):
        super().__init__(
            title=i18n.get("gift_codes.add_code"),
            custom_id=f"gift_code_modal_{mode}"
        )
        
        self.code_input = ui.TextInput(
            label=i18n.get("gift_codes.code"),
            placeholder="Enter gift code",
            required=True,
            max_length=50
        )
        
        self.add_item(self.code_input)


class EventModal(BaseModal):
    """Modal for event operations."""
    
    def __init__(self, mode: str = "add", event_data: Optional[Dict] = None):
        title = i18n.get("events.create_event") if mode == "add" else i18n.get("events.edit_title")
        super().__init__(title=title, custom_id=f"event_modal_{mode}")
        
        self.name_input = ui.TextInput(
            label=i18n.get("events.event_name"),
            placeholder="Enter event name",
            default_value=event_data.get("name", "") if event_data else "",
            required=True,
            max_length=100
        )
        
        self.date_input = ui.TextInput(
            label=i18n.get("events.event_date"),
            placeholder="YYYY-MM-DD",
            default_value=event_data.get("event_date", "") if event_data else "",
            required=True,
            max_length=10
        )
        
        self.time_input = ui.TextInput(
            label=i18n.get("events.event_time"),
            placeholder="HH:MM",
            default_value=event_data.get("event_time", "") if event_data else "",
            required=False,
            max_length=5
        )
        
        self.location_input = ui.TextInput(
            label=i18n.get("events.event_location"),
            placeholder="Enter event location",
            default_value=event_data.get("location", "") if event_data else "",
            required=False,
            max_length=100
        )
        
        self.add_item(self.name_input)
        self.add_item(self.date_input)
        self.add_item(self.time_input)
        self.add_item(self.location_input)

    async def on_submit(self, interaction: discord.Interaction):
        """Handle event submission."""
        from core.database import db
        from core.audit_log import audit_log, AuditCategory

        name = self.name_input.value.strip()
        date = self.date_input.value.strip()
        time = self.time_input.value.strip()
        location = self.location_input.value.strip()

        try:
            if self.mode == "add":
                cursor = await db.execute(
                    """ INSERT INTO events (name, event_date, event_time, location, created_by)
                       VALUES (?, ?, ?, ?, ?)""",
                    (name, date, time, location, str(interaction.user.id))
                )
                await db.commit()
            else:
                event_id = self.event_data.get("id") if self.event_data else None
                if event_id:
                    await db.execute(
                        """UPDATE events SET name = ?, event_date = ?, event_time = ?, location = ? WHERE id = ?""",
                        (name, date, time, location, event_id)
                    )
                    await db.commit()

            await interaction.response.send_message(
                f"✅ {i18n.get('messages.success')}\n**{name}**",
                ephemeral=True
            )

            await audit_log.log(
                user_id=str(interaction.user.id),
                user_name=str(interaction.user),
                action="create_event" if self.mode == "add" else "edit_event",
                category=AuditCategory.EVENTS,
                details={"name": name, "date": date}
            )

        except Exception:
            import logging
            logging.exception("EventModal failed")
            await interaction.response.send_message(f"❌ {i18n.get('messages.error')}", ephemeral=True)

    async def on_error(self, interaction, error):
        import logging
        logging.exception("EventModal error")
        if not interaction.response.is_done():
            await interaction.response.send_message("حدث خطأ.", ephemeral=True)


class NotificationModal(BaseModal):
    """Modal for notification operations."""
    
    def __init__(self, mode: str = "add", notification_data: Optional[Dict] = None):
        title = i18n.get("notifications.add_notification") if mode == "add" else i18n.get("notifications.edit_notification")
        super().__init__(title=title, custom_id=f"notification_modal_{mode}")
        
        self.name_input = ui.TextInput(
            label=i18n.get("notifications.notification_type"),
            placeholder="Enter notification name",
            default_value=notification_data.get("name", "") if notification_data else "",
            required=True,
            max_length=100
        )
        
        self.message_input = ui.TextInput(
            label=i18n.get("notifications.notification_message"),
            placeholder="Enter notification message",
            default_value=notification_data.get("message", "") if notification_data else "",
            required=True,
            max_length=500
        )
        
        self.time_input = ui.TextInput(
            label=i18n.get("notifications.notification_time"),
            placeholder="HH:MM",
            default_value=notification_data.get("scheduled_time", "") if notification_data else "",
            required=False,
            max_length=5
        )
        
        self.add_item(self.name_input)
        self.add_item(self.message_input)
        self.add_item(self.time_input)


class MinisterModal(BaseModal):
    """Modal for minister operations."""
    
    def __init__(self, mode: str = "add", minister_data: Optional[Dict] = None):
        title = i18n.get("ministers.add_minister") if mode == "add" else i18n.get("ministers.edit_minister")
        super().__init__(title=title, custom_id=f"minister_modal_{mode}")
        
        self.title_input = ui.TextInput(
            label=i18n.get("ministers.minister_title"),
            placeholder="Enter position title",
            default_value=minister_data.get("title", "") if minister_data else "",
            required=True,
            max_length=100
        )
        
        self.add_item(self.title_input)


class ThemeModal(BaseModal):
    """Modal for theme customization."""
    
    def __init__(self, setting_key: str, current_value: str = ""):
        super().__init__(
            title=i18n.get("themes.title"),
            custom_id=f"theme_modal_{setting_key}"
        )
        
        self.setting_key = setting_key
        
        self.value_input = ui.TextInput(
            label=setting_key,
            placeholder="Enter value",
            default_value=current_value,
            required=True,
            max_length=100
        )
        
        self.add_item(self.value_input)


class OwnerPanelModal(BaseModal):
    """Modal for owner panel text editing."""
    
    def __init__(
        self,
        title: str,
        text_key: str,
        current_value_ar: str = "",
        current_value_en: str = "",
        multiline: bool = False
    ):
        super().__init__(title=title, custom_id=f"owner_panel_modal_{text_key}")
        
        self.text_key = text_key
        
        self.ar_input = ui.TextInput(
            label=f"{i18n.get('language.arabic')} (AR)",
            placeholder="Enter Arabic text",
            default_value=current_value_ar,
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph if multiline else discord.TextStyle.short
        )
        
        self.en_input = ui.TextInput(
            label=f"{i18n.get('language.english')} (EN)",
            placeholder="Enter English text",
            default_value=current_value_en,
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph if multiline else discord.TextStyle.short
        )
        
        self.add_item(self.ar_input)
        self.add_item(self.en_input)


class PermissionModal(BaseModal):
    """Modal for permission assignment."""
    
    def __init__(self):
        super().__init__(
            title=i18n.get("permissions.assign_role"),
            custom_id="permission_modal"
        )
        
        self.user_id_input = ui.TextInput(
            label="User ID",
            placeholder="Enter Discord user ID",
            required=True,
            max_length=50
        )
        
        self.role_input = ui.TextInput(
            label=i18n.get("permissions.title"),
            placeholder="owner, global_admin, server_admin, alliance_admin, member",
            required=True,
            max_length=50
        )
        
        self.add_item(self.user_id_input)
        self.add_item(self.role_input)


class AttendanceModal(BaseModal):
    """Modal for attendance recording."""
    
    def __init__(self, event_id: int):
        super().__init__(
            title=i18n.get("attendance.record_attendance"),
            custom_id=f"attendance_modal_{event_id}"
        )
        
        self.event_id = event_id
        
        self.fid_input = ui.TextInput(
            label=i18n.get("players.fid"),
            placeholder="Enter player FID",
            required=True,
            max_length=50
        )
        
        self.add_item(self.fid_input)


class BearDamageModal(BaseModal):
    """Modal for bear damage recording."""
    
    def __init__(self, hunt_id: int):
        super().__init__(
            title=i18n.get("bear_tracking.damage_record"),
            custom_id=f"bear_damage_modal_{hunt_id}"
        )
        
        self.hunt_id = hunt_id
        
        self.player_name_input = ui.TextInput(
            label=i18n.get("players.player_name"),
            placeholder="Enter player name",
            required=True,
            max_length=100
        )
        
        self.damage_input = ui.TextInput(
            label=i18n.get("bear_tracking.total_damage"),
            placeholder="Enter damage amount",
            required=True,
            max_length=10
        )
        
        self.add_item(self.player_name_input)
        self.add_item(self.damage_input)


class CustomTextModal(BaseModal):
    """Modal for custom text editing."""
    
    def __init__(self, text_key: str, current_value: str = ""):
        super().__init__(
            title=f"{i18n.get('owner_panel.edit_title')}: {text_key}",
            custom_id=f"custom_text_modal_{text_key}"
        )
        
        self.text_key = text_key
        
        self.text_input = ui.TextInput(
            label="Text",
            placeholder="Enter new text",
            default_value=current_value,
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph
        )
        
        self.add_item(self.text_input)
