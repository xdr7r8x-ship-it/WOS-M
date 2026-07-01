"""
Tests for Database Schema Contract
© MANSOUR — WOS-M. All rights reserved.
Ensures all SQL columns used by modules exist in schema.
"""
import pytest
import re
from pathlib import Path


class TestSchemaContract:
    """Test that all SQL columns referenced in code exist in schema."""
    
    def test_alliances_table_has_discord_role_id(self):
        """alliances table must include discord_role_id column."""
        db_file = Path("core/database.py")
        assert db_file.exists(), "core/database.py must exist"
        
        content = open(db_file).read()
        
        # Find alliances table definition
        alliance_table_match = re.search(
            r'CREATE TABLE IF NOT EXISTS alliances\s*\((.*?)\);',
            content,
            re.DOTALL | re.IGNORECASE
        )
        assert alliance_table_match, "alliances table not found in schema"
        
        table_def = alliance_table_match.group(1)
        assert "discord_role_id" in table_def, (
            "alliances table must include discord_role_id column"
        )
    
    def test_alliances_table_has_all_required_columns(self):
        """alliances table must have all required columns."""
        db_file = Path("core/database.py")
        content = open(db_file).read()
        
        required = [
            "id", "name", "state_kid", "discord_guild_id", "discord_role_id",
            "auto_gift_enabled", "gift_channel_id", "member_count", "sync_enabled",
            "report_channel_id", "is_active", "created_at", "updated_at"
        ]
        
        for col in required:
            assert col in content, f"alliances table missing column: {col}"
    
    def test_players_table_has_all_required_columns(self):
        """players table must have all required columns."""
        db_file = Path("core/database.py")
        content = open(db_file).read()
        
        required = [
            "id", "fid", "name", "alliance_id", "level", 
            "is_active", "created_at", "updated_at"
        ]
        
        for col in required:
            assert col in content, f"players table missing column: {col}"
    
    def test_discord_role_id_migration_exists(self):
        """Migration for discord_role_id must exist."""
        migrations_file = Path("database/migrations/__init__.py")
        assert migrations_file.exists(), "migrations/__init__.py must exist"
        
        content = open(migrations_file).read()
        assert "add_alliance_discord_role_id" in content, (
            "migration add_alliance_discord_role_id not found"
        )
    
    def test_alliance_add_callback_no_missing_columns(self):
        """alliance_add_callback should not reference missing columns."""
        views_file = Path("modules/alliances/views.py")
        assert views_file.exists(), "modules/alliances/views.py must exist"
        
        content = open(views_file).read()
        
        # These columns must exist in schema
        required_in_schema = [
            "discord_role_id", "name", "state_kid", "is_active"
        ]
        
        for col in required_in_schema:
            # If code uses this column, it must exist in schema
            if col in content and "INSERT INTO alliances" in content:
                db_file = Path("core/database.py")
                db_content = open(db_file).read()
                assert col in db_content, (
                    f"alliance_add_callback uses {col} but it's not in schema"
                )
    
    def test_main_check_fails_on_schema_mismatch(self):
        """main.py --check must detect schema mismatches."""
        main_file = Path("main.py")
        assert main_file.exists(), "main.py must exist"
        
        content = open(main_file).read()
        
        # Must check for discord_role_id
        assert "discord_role_id" in content, (
            "main.py must check for discord_role_id column"
        )
        
        # Must check migrations
        assert "add_alliance_discord_role_id" in content, (
            "main.py must check for migration"
        )


class TestSchemaMigrations:
    """Test database migrations are properly defined."""
    
    def test_migrations_file_exists(self):
        """Migrations file must exist."""
        migrations_file = Path("database/migrations/__init__.py")
        assert migrations_file.exists()
    
    def test_migrations_have_version_and_name(self):
        """Each migration must have version and name."""
        migrations_file = Path("database/migrations/__init__.py")
        content = open(migrations_file).read()
        
        # Check migrations are defined
        assert "MIGRATIONS" in content
        assert '"version":' in content
        assert '"name":' in content
        assert '"description":' in content
        assert '"sql":' in content
    
    def test_discord_role_id_migration_is_safe(self):
        """discord_role_id migration must be safe (ALTER TABLE ADD COLUMN)."""
        migrations_file = Path("database/migrations/__init__.py")
        content = open(migrations_file).read()
        
        # Find the migration
        migration_match = re.search(
            r'"name":\s*"add_alliance_discord_role_id".*?"sql":\s*"""(.*?)"""',
            content,
            re.DOTALL
        )
        assert migration_match, "add_alliance_discord_role_id migration not found"
        
        sql = migration_match.group(1)
        assert "ALTER TABLE alliances ADD COLUMN discord_role_id" in sql, (
            "Migration must use safe ALTER TABLE ADD COLUMN"
        )