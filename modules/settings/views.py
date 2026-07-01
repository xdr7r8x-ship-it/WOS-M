"""
WOS-M Settings Module
© MANSOUR — WOS-M. All rights reserved.
"""
import discord
from core.bot import WOSMBot


async def settings_general_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for settings_general."""
    await interaction.response.send_message("إعدادات عامة.", ephemeral=True)


async def settings_api_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for settings_api."""
    await interaction.response.send_message("إعدادات API.", ephemeral=True)


async def settings_save_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for settings_save."""
    await interaction.response.send_message("تم حفظ الإعدادات.", ephemeral=True)


async def settings_reset_callback(bot: WOSMBot, interaction: discord.Interaction):
    """Callback for settings_reset."""
    await interaction.response.send_message("تم إعادة تعيين الإعدادات.", ephemeral=True)
