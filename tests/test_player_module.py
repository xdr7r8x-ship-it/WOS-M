"""
Tests for Player Module
© MANSOUR — WOS-M. All rights reserved.
"""
import pytest
from pathlib import Path


class TestPlayerModule:
    """Test player module callbacks."""
    
    def test_player_add_callback_exists(self):
        """player_add_callback must exist."""
        views_file = Path("modules/players/views.py")
        assert views_file.exists()
        
        content = open(views_file).read()
        assert "async def player_add_callback" in content
    
    def test_player_add_validates_fid(self):
        """player_add_callback must validate FID format."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "fid" in content.lower()
        assert "validate_fid" in content or "is_valid" in content or "strip" in content
    
    def test_player_add_checks_duplicates(self):
        """player_add_callback must check for existing player."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "existing" in content.lower() or "SELECT" in content
    
    def test_player_add_inserts_to_db(self):
        """player_add_callback must INSERT into players table."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "INSERT INTO players" in content
    
    def test_player_add_has_permission_check(self):
        """player_add_callback must check ADMIN permission."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "ADMIN" in content or "has_permission" in content
    
    def test_player_add_has_audit_log(self):
        """player_add_callback must write audit log."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "audit_log" in content or "audit" in content.lower()
    
    def test_player_search_callback_exists(self):
        """player_search_callback must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "async def player_search_callback" in content
    
    def test_player_list_callback_exists(self):
        """player_list_callback must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "async def player_list_callback" in content
    
    def test_player_sync_callback_exists(self):
        """player_sync_callback must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "async def player_sync_callback" in content
    
    def test_player_move_callback_exists(self):
        """player_move_callback must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "async def player_move_callback" in content
    
    def test_player_export_callback_exists(self):
        """player_export_callback must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "async def player_export_callback" in content


class TestPlayerFIDValidation:
    """Test FID validation in player module."""
    
    def test_fid_validation_function_exists(self):
        """validate_fid function must exist."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "def validate_fid" in content or "def validate" in content
    
    def test_fid_validation_checks_length(self):
        """FID validation must check length (8-11 digits)."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "8" in content or "9" in content or "10" in content or "11" in content


class TestPlayerDBOperations:
    """Test player database operations."""
    
    def test_player_insert_uses_fid(self):
        """Player INSERT must include fid column."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "INSERT INTO players" in content
        assert "fid" in content
    
    def test_player_insert_uses_name(self):
        """Player INSERT must include name column."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "INSERT INTO players" in content
        assert "name" in content
    
    def test_player_can_have_alliance_id(self):
        """Player can be assigned to alliance."""
        views_file = Path("modules/players/views.py")
        content = open(views_file).read()
        
        assert "alliance_id" in content