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
    """Check system before running with comprehensive validation."""
    print("🔍 WOS-M System Check")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # Check .env file
    if not os.path.exists(".env"):
        warnings.append("⚠️  .env file not found, using defaults")
    else:
        print("✅ .env file found")
    
    # Check required env vars
    if not os.getenv("DISCORD_BOT_TOKEN"):
        issues.append("❌ DISCORD_BOT_TOKEN not set - REQUIRED")
    else:
        print("✅ DISCORD_BOT_TOKEN configured")
    
    # Check locales
    locales_dir = Path(__file__).parent / "locales"
    if locales_dir.exists():
        locale_files = list(locales_dir.glob("*.json"))
        print(f"✅ Found {len(locale_files)} locale files (ar.json, en.json)")
        
        # Validate locale content
        import json
        for lf in locale_files:
            with open(lf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "bot" in data and "dashboard" in data and "messages" in data:
                    print(f"   ✅ {lf.name}: Valid structure")
                else:
                    issues.append(f"❌ {lf.name}: Missing required keys")
    else:
        issues.append("❌ Locales directory not found")
    
    # Check for hardcoded strings in code
    print("\n📋 Checking for hardcoded user-facing strings...")
    code_files = list(Path(__file__).parent.glob("modules/**/*.py"))
    code_files += list(Path(__file__).parent.glob("core/**/*.py"))
    code_files += list(Path(__file__).parent.glob("views/**/*.py"))
    
    hardcoded_patterns = []
    for cf in code_files:
        if cf.name == "__init__.py":
            continue
        with open(cf, "r", encoding="utf-8") as f:
            content = f.read()
            # Check for Arabic text that's not in f-strings or comments
            if any(arabic in content for arabic in ['"التحالفات"', '"اللاعبين"', '"المالك"']):
                if 'i18n.get' not in content and "# " not in content.split('"التحالفات"')[0][-50:]:
                    hardcoded_patterns.append(cf.name)
    
    if hardcoded_patterns:
        warnings.append(f"⚠️  Potential hardcoded strings in: {', '.join(set(hardcoded_patterns[:3]))}")
    else:
        print("✅ No obvious hardcoded user-facing strings found")
    
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
    print("\n📦 Checking dependencies...")
    deps = {
        "discord": "discord.py",
        "aiosqlite": "aiosqlite",
        "aiohttp": "aiohttp",
        "dotenv": "python-dotenv"
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            issues.append(f"❌ {name} not installed")
    
    # Check slash commands
    print("\n📡 Checking slash commands...")
    bot_file = Path(__file__).parent / "core" / "bot.py"
    if bot_file.exists():
        with open(bot_file, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Count @tree.command decorators
            import re
            commands = re.findall(r'name\s*=\s*["\']([^"\']+)', content)
            commands = [c for c in commands if c in ["wos", "test", "help", "start"]]
            
            if "wos" in commands:
                print(f"✅ /wos command registered")
            else:
                issues.append("❌ /wos command not found")
            
            other_commands = [c for c in commands if c != "wos"]
            if other_commands:
                issues.append(f"❌ Additional commands found: {', '.join(['/' + c for c in other_commands])}")
            else:
                print("✅ Only /wos command (no additional slash commands)")
    
    # Check Back/Home buttons in views
    print("\n🔘 Checking Back and Home buttons...")
    view_files = list(Path(__file__).parent.glob("modules/**/views.py"))
    views_with_nav = 0
    for vf in view_files:
        with open(vf, "r", encoding="utf-8") as f:
            content = f.read()
            if "back" in content.lower() and "home" in content.lower():
                views_with_nav += 1
    
    if views_with_nav >= 5:
        print(f"✅ Navigation buttons found in {views_with_nav} view modules")
    else:
        warnings.append(f"⚠️  Only {views_with_nav} views with navigation buttons")
    
    # Check gift codes engine
    print("\n🎁 Checking Gift Code Redemption system...")
    gc_engine = Path(__file__).parent / "modules" / "gift_codes" / "redemption_engine.py"
    if gc_engine.exists():
        with open(gc_engine, "r", encoding="utf-8") as f:
            content = f.read()
            if "auto_redeem_for_alliance" in content and "batch_redeem" in content:
                print("✅ Auto Redemption engine implemented")
            else:
                issues.append("❌ Gift Code Redemption engine incomplete")
    
    # Summary
    print("\n" + "=" * 60)
    
    if warnings:
        print("⚠️  Warnings:")
        for w in warnings:
            print(f"   {w}")
    
    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("✅ All critical checks passed!")
    print("⚠️  Some warnings may need attention but are non-blocking")
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
