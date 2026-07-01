#!/usr/bin/env python3
"""
WOS-M Main Entry Point
© MANSOUR — WOS-M. All rights reserved.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

import dotenv

# Load environment variables
dotenv.load_dotenv()

from config.settings import settings
from core.bot import WOSMBot

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    log_dir = Path(__file__).parent / "data" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, settings.logging.level),
        format=settings.logging.format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(settings.logging.file),
        ]
    )
    
    # Reduce discord logging
    logging.getLogger("discord").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)


async def run_bot():
    """Run the bot."""
    bot = WOSMBot()
    
    token = os.getenv("DISCORD_BOT_TOKEN") or settings.bot.token
    
    if not token:
        logger.error("No bot token found! Set DISCORD_BOT_TOKEN in .env file.")
        sys.exit(1)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await bot.close()


def check_system():
    """Check system before running."""
    print("🔍 WOS-M System Check")
    print("=" * 50)
    
    issues = []
    
    # Check .env file
    if not os.path.exists(".env"):
        print("⚠️  .env file not found, using defaults")
    
    # Check required env vars
    if not os.getenv("DISCORD_BOT_TOKEN"):
        issues.append("❌ DISCORD_BOT_TOKEN not set")
    else:
        print("✅ DISCORD_BOT_TOKEN configured")
    
    # Check locales
    locales_dir = Path(__file__).parent / "locales"
    if locales_dir.exists():
        locale_files = list(locales_dir.glob("*.json"))
        print(f"✅ Found {len(locale_files)} locale files")
    else:
        issues.append("❌ Locales directory not found")
    
    # Check data directory
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory: {data_dir}")
    
    # Check Python version
    if sys.version_info < (3, 10):
        issues.append(f"❌ Python 3.10+ required, found {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
    
    # Check modules
    try:
        import discord
        print(f"✅ discord.py installed")
    except ImportError:
        issues.append("❌ discord.py not installed")
    
    try:
        import aiosqlite
        print("✅ aiosqlite installed")
    except ImportError:
        issues.append("❌ aiosqlite not installed")
    
    try:
        import aiohttp
        print("✅ aiohttp installed")
    except ImportError:
        issues.append("❌ aiohttp not installed")
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        issues.append("❌ python-dotenv not installed")
    
    print("=" * 50)
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("✅ All checks passed!")
    return True


def main():
    """Main entry point."""
    if "--check" in sys.argv:
        if check_system():
            sys.exit(0)
        else:
            sys.exit(1)
    
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)


if __name__ == "__main__":
    main()
