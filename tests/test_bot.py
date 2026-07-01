"""
WOS-M Test Suite
© MANSOUR — WOS-M. All rights reserved.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestI18n:
    """Test internationalization system."""
    
    def test_locales_exist(self):
        """Test that locale files exist."""
        locales_dir = Path(__file__).parent.parent / "locales"
        assert (locales_dir / "ar.json").exists()
        assert (locales_dir / "en.json").exists()
    
    def test_locale_format(self):
        """Test that locale files are valid JSON."""
        import json
        
        locales_dir = Path(__file__).parent.parent / "locales"
        
        for locale_file in locales_dir.glob("*.json"):
            with open(locale_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert "bot" in data
                assert "dashboard" in data
                assert "buttons" in data
                assert "messages" in data


class TestPermissions:
    """Test permission system."""
    
    def test_permission_levels(self):
        """Test permission level hierarchy."""
        from core.permissions import PermissionLevel
        
        assert PermissionLevel.OWNER.value == 1
        assert PermissionLevel.GLOBAL_ADMIN.value == 2
        assert PermissionLevel.SERVER_ADMIN.value == 3
        assert PermissionLevel.ALLIANCE_ADMIN.value == 4
        assert PermissionLevel.MEMBER.value == 5
        
        # Owner should be higher than Member
        assert PermissionLevel.OWNER > PermissionLevel.MEMBER
        assert PermissionLevel.GLOBAL_ADMIN > PermissionLevel.MEMBER


class TestGiftCodes:
    """Test gift code system."""
    
    def test_status_constants(self):
        """Test gift code status constants."""
        from modules.gift_codes.models import GiftCodeStatus
        
        assert GiftCodeStatus.PENDING.value == "pending"
        assert GiftCodeStatus.VALID.value == "valid"
        assert GiftCodeStatus.REDEEMED.value == "redeemed"
        assert GiftCodeStatus.FAILED.value == "failed"
    
    def test_validation_engine_pattern(self):
        """Test validation engine code pattern."""
        import re
        from modules.gift_codes.validation_engine import ValidationEngine
        
        engine = ValidationEngine()
        pattern = engine.CODE_PATTERN
        
        # Valid codes
        assert pattern.match("ABC123")
        assert pattern.match("ABCD1234")
        
        # Invalid codes (too short, special chars)
        assert not pattern.match("ABC")
        assert not pattern.match("ABC-123")
        assert not pattern.match("abc123")


class TestProcessQueue:
    """Test process queue system."""
    
    def test_queue_priority(self):
        """Test queue priority levels."""
        from core.process_queue import QueuePriority
        
        assert QueuePriority.GIFT_VALIDATE < QueuePriority.GIFT_REDEEM
        assert QueuePriority.GIFT_REDEEM < QueuePriority.PLAYER_ADD
        assert QueuePriority.PLAYER_ADD < QueuePriority.ALLIANCE_UPDATE
        assert QueuePriority.ALLIANCE_UPDATE < QueuePriority.REPORT_GENERATION


class TestFeatureRegistry:
    """Test feature registry system."""
    
    def test_default_features_exist(self):
        """Test that default features are defined."""
        from core.feature_registry import FeatureRegistry
        
        assert len(FeatureRegistry.DEFAULT_FEATURES) > 0
        
        # Check required features exist
        feature_keys = [f["key"] for f in FeatureRegistry.DEFAULT_FEATURES]
        assert "alliances" in feature_keys
        assert "players" in feature_keys
        assert "gift_codes" in feature_keys
        assert "owner_panel" in feature_keys
    
    def test_feature_manifest(self):
        """Test feature manifest structure."""
        from core.feature_registry import FeatureManifest
        
        manifest = FeatureManifest(
            key="test_feature",
            name_ar="اختبار",
            name_en="Test",
            description_ar="وصف الاختبار",
            description_en="Test description",
            icon="🧪",
            enabled=True,
            required_permission="member"
        )
        
        data = manifest.to_dict()
        assert data["key"] == "test_feature"
        assert data["name"]["ar"] == "اختبار"
        assert data["name"]["en"] == "Test"
        assert data["enabled"] == True


class TestConfig:
    """Test configuration system."""
    
    def test_settings_load(self):
        """Test settings can be loaded."""
        from config.settings import Settings
        
        settings = Settings()
        assert settings.bot.owner_name == "MANSOUR"
        assert settings.default_language == "ar"
        assert settings.theme_color_primary == 0x3498db


class TestDatabase:
    """Test database system."""
    
    @pytest.mark.asyncio
    async def test_database_tables(self):
        """Test that database tables are defined."""
        from core.database import Database
        
        db = Database()
        # Tables should be created during initialization
        assert db._db is None  # Not initialized yet


# Test fixtures
@pytest.fixture
def mock_interaction():
    """Create a mock Discord interaction."""
    interaction = Mock()
    interaction.user.id = 123456789
    interaction.user.name = "TestUser"
    interaction.response = Mock()
    interaction.response.send_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    interaction.followup = Mock()
    interaction.followup.send = AsyncMock()
    return interaction


@pytest.fixture
def mock_bot():
    """Create a mock bot."""
    bot = Mock()
    bot.owner_id = "123456789"
    bot.owner_name = "MANSOUR"
    bot.owner_discord = "DANGER_600"
    return bot


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
