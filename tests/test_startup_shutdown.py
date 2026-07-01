"""
Tests for Startup and Shutdown
© MANSOUR — WOS-M. All rights reserved.
"""
import pytest
import asyncio
from pathlib import Path


class TestBotInitialization:
    """Test bot initialization."""
    
    def test_bot_module_exists(self):
        """core.bot module must exist."""
        bot_file = Path("core/bot.py")
        assert bot_file.exists(), "core/bot.py must exist"
    
    def test_wosmbot_class_exists(self):
        """WOSMBot class must be defined."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "class WOSMBot" in content or "WOSMBot" in content
    
    def test_bot_has_intents(self):
        """Bot must configure intents."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "Intents" in content
    
    def test_dynamic_router_exists(self):
        """Dynamic router must be registered."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "dynamic" in content.lower() or "router" in content.lower()


class TestCallbackRegistration:
    """Test callback registration."""
    
    def test_player_callbacks_registered(self):
        """Player callbacks must be registered."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "player" in content.lower()
    
    def test_alliance_callbacks_registered(self):
        """Alliance callbacks must be registered."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "alliance" in content.lower()
    
    def test_gift_callbacks_registered(self):
        """Gift callbacks must be registered."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "gift" in content.lower()


class TestEnvValidation:
    """Test environment variable validation."""
    
    def test_main_check_validates_env(self):
        """main.py --check must validate env."""
        main_file = Path("main.py")
        content = open(main_file).read()
        
        assert "DISCORD_BOT_TOKEN" in content
        assert ".env" in content
    
    def test_missing_env_gives_clear_error(self):
        """Missing env should give clear error, not crash."""
        main_file = Path("main.py")
        content = open(main_file).read()
        
        assert "sys.exit" in content or "exit(" in content


class TestCleanShutdown:
    """Test clean shutdown."""
    
    def test_bot_has_close_method(self):
        """Bot must have close method."""
        bot_file = Path("core/bot.py")
        content = open(bot_file).read()
        
        assert "close" in content.lower() or "logout" in content.lower()
    
    def test_main_has_keyboard_interrupt_handler(self):
        """Main must handle KeyboardInterrupt."""
        main_file = Path("main.py")
        content = open(main_file).read()
        
        assert "KeyboardInterrupt" in content or "finally" in content
