"""
WOS-M Database Seed
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
from datetime import datetime

from core.database import db


async def seed_initial_data():
    """Seed initial data into the database."""
    
    # Set default settings
    default_settings = [
        ("language", "ar"),
        ("bot_name", "WOS-M"),
        ("bot_version", "1.0.0"),
    ]
    
    for key, value in default_settings:
        await db.execute(
            "INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    # Set default theme settings
    default_themes = [
        ("primary_color", "0x3498db"),
        ("success_color", "0x2ecc71"),
        ("warning_color", "0xf39c12"),
        ("error_color", "0xe74c3c"),
        ("info_color", "0x1abc9c"),
        ("footer_text", "© MANSOUR — WOS-M"),
    ]
    
    for key, value in default_themes:
        await db.execute(
            "INSERT OR IGNORE INTO theme_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    
    # Add default language settings
    languages = [
        ("ar", True, True),
        ("en", False, True),
    ]
    
    for locale, is_default, is_active in languages:
        await db.execute(
            "INSERT OR IGNORE INTO language_settings (locale, is_default, is_active) VALUES (?, ?, ?)",
            (locale, is_default, is_active)
        )
    
    # Seed default custom buttons
    default_buttons = [
        ("alliances", "🏰", "dashboard.alliances", 0, True, None, "member"),
        ("players", "👥", "dashboard.players", 1, True, None, "member"),
        ("gift_codes", "🎁", "dashboard.auto_gift", 2, True, None, "member"),
        ("events", "📅", "dashboard.events", 3, True, None, "member"),
        ("attendance", "✅", "dashboard.attendance", 4, True, None, "member"),
        ("bear_tracking", "🐻", "dashboard.bear_tracking", 5, True, None, "member"),
        ("ministers", "👔", "dashboard.ministers", 6, True, None, "member"),
        ("notifications", "🔔", "dashboard.notifications", 7, True, None, "member"),
        ("themes", "🎨", "dashboard.themes", 8, True, None, "member"),
        ("permissions", "🔐", "dashboard.permissions", 9, True, None, "alliance_admin"),
        ("maintenance", "🔧", "dashboard.maintenance", 10, True, None, "global_admin"),
        ("owner_panel", "👑", "dashboard.owner_panel", 11, True, None, "owner"),
        ("language", "🌐", "dashboard.language", 12, True, None, "member"),
        ("settings", "⚙️", "dashboard.settings", 13, True, None, "member"),
    ]
    
    for btn_key, icon, label_key, position, is_enabled, linked, perm in default_buttons:
        await db.execute(
            """INSERT OR IGNORE INTO custom_buttons 
               (button_key, icon, label_key, position, is_enabled, linked_feature, required_permission) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (btn_key, icon, label_key, position, is_enabled, linked, perm)
        )
    
    await db.commit()
    print("✅ Database seeded successfully!")


async def run_seed():
    """Run the seed function."""
    await db.initialize()
    await seed_initial_data()
    await db.close()


if __name__ == "__main__":
    asyncio.run(run_seed())
