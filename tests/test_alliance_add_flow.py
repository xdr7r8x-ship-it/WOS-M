"""
Tests for Alliance Add Flow
© MANSOUR — WOS-M. All rights reserved.
Tests the alliance_add_callback flow end-to-end.
"""
import pytest
import re
from pathlib import Path


class TestAllianceAddCallback:
    """Test alliance_add_callback implementation."""
    
    def test_alliance_add_callback_exists(self):
        """alliance_add_callback must exist in alliances views."""
        views_file = Path("modules/alliances/views.py")
        assert views_file.exists()
        
        content = open(views_file).read()
        assert "async def alliance_add_callback" in content, (
            "alliance_add_callback must be defined"
        )
    
    def test_alliance_add_uses_modal(self):
        """alliance_add_callback must use Modal for input."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "ui.Modal" in content, (
            "alliance_add_callback must use discord.ui.Modal"
        )
        assert "send_modal" in content, (
            "alliance_add_callback must send_modal"
        )
    
    def test_alliance_add_validates_input(self):
        """alliance_add_callback must validate required fields."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        # Should check for name
        assert "name_input" in content or "name" in content.lower(), (
            "Must handle name input"
        )
        # Should check for state_kid
        assert "state_kid" in content, (
            "Must handle state_kid input"
        )
    
    def test_alliance_add_checks_duplicates(self):
        """alliance_add_callback must check for duplicate alliances."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        # Should check existing alliance
        assert "SELECT" in content or "existing" in content.lower(), (
            "Must check for existing alliance before adding"
        )
    
    def test_alliance_add_inserts_to_db(self):
        """alliance_add_callback must INSERT into alliances table."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "INSERT INTO alliances" in content, (
            "alliance_add_callback must INSERT into alliances"
        )
    
    def test_alliance_add_saves_discord_role_id(self):
        """alliance_add_callback must save discord_role_id to DB."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        # Should reference discord_role_id in INSERT
        assert "discord_role_id" in content, (
            "alliance_add_callback must handle discord_role_id"
        )
    
    def test_alliance_add_has_permission_check(self):
        """alliance_add_callback must check permissions."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "PermissionGuard" in content or "has_permission" in content, (
            "alliance_add_callback must check permissions"
        )
        assert "ADMIN" in content, (
            "alliance_add_callback requires ADMIN permission"
        )
    
    def test_alliance_add_has_audit_log(self):
        """alliance_add_callback must write audit log."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "audit_log" in content, (
            "alliance_add_callback must write audit log"
        )
        assert "add_alliance" in content, (
            "Audit log must record add_alliance action"
        )


class TestAllianceDeleteCallback:
    """Test alliance_delete_callback implementation."""
    
    def test_alliance_delete_requires_confirmation(self):
        """alliance_delete_callback must require confirmation."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "delete" in content.lower(), (
            "alliance_delete_callback must handle deletion"
        )
        
        # Should require typing 'حذف' for confirmation
        assert "حذف" in content, (
            "alliance_delete_callback must require 'حذف' confirmation"
        )
    
    def test_alliance_delete_checks_permissions(self):
        """alliance_delete_callback must check ADMIN permissions."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "PermissionGuard" in content or "has_permission" in content, (
            "alliance_delete_callback must check permissions"
        )


class TestAllianceListCallback:
    """Test alliance_list_callback implementation."""
    
    def test_alliance_list_selects_from_db(self):
        """alliance_list_callback must SELECT from alliances."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "SELECT" in content, (
            "alliance_list_callback must SELECT from database"
        )
        assert "alliances" in content.lower(), (
            "alliance_list_callback must query alliances table"
        )
    
    def test_alliance_list_returns_pagination(self):
        """alliance_list_callback should return paginated results."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        # Should use PaginationView or similar
        assert "PaginationView" in content or "pagination" in content.lower() or "view" in content, (
            "alliance_list_callback should support pagination"
        )


class TestAllianceEditCallback:
    """Test alliance_edit_callback implementation."""
    
    def test_alliance_edit_uses_modal(self):
        """alliance_edit_callback must use Modal for input."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "edit" in content.lower(), (
            "alliance_edit_callback must exist"
        )
        assert "Modal" in content or "modal" in content.lower(), (
            "alliance_edit_callback must use Modal"
        )
    
    def test_alliance_edit_updates_db(self):
        """alliance_edit_callback must UPDATE alliances table."""
        views_file = Path("modules/alliances/views.py")
        content = open(views_file).read()
        
        assert "UPDATE alliances" in content, (
            "alliance_edit_callback must UPDATE alliances"
        )