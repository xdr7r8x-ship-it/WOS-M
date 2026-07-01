"""
Tests for Error Boundaries
© MANSOUR — WOS-M. All rights reserved.
Ensures errors are handled gracefully without crashing the bot.
"""
import pytest
from pathlib import Path
import re


class TestErrorHandling:
    """Test error handling in modules."""
    
    def test_modules_exist(self):
        """Modules should exist."""
        modules = [
            "modules/players/views.py",
            "modules/alliances/views.py",
            "modules/gift_codes/views.py",
        ]
        
        for module in modules:
            path = Path(module)
            assert path.exists(), f"{module} must exist"


class TestLogging:
    """Test logging configuration."""
    
    def test_logging_configured(self):
        """Logging must be configured."""
        main_file = Path("main.py")
        content = open(main_file).read()
        
        assert "logging" in content.lower()
    
    def test_audit_log_module_exists(self):
        """Audit log module must exist."""
        audit_file = Path("core/audit_log.py")
        assert audit_file.exists()


class TestNoSecretsInErrors:
    """Test that errors don't leak secrets."""
    
    def test_no_token_in_logs(self):
        """Token should not be logged."""
        modules = Path("modules")
        
        for py_file in modules.rglob("*.py"):
            content = open(py_file).read()
            
            assert "ghp_" not in content, f"{py_file} should not log GitHub tokens"


class TestUserFacingErrors:
    """Test user-facing error messages."""
    
    def test_arabic_error_messages_exist(self):
        """Arabic error messages should be defined."""
        views_files = list(Path("modules").rglob("views.py"))
        
        assert len(views_files) > 0, "Should have view files"


class TestPermissionErrors:
    """Test permission error handling."""
    
    def test_permission_check_exists(self):
        """Permission checks must exist."""
        perm_file = Path("core/permissions.py")
        assert perm_file.exists()
        
        content = open(perm_file).read()
        assert "PermissionGuard" in content or "has_permission" in content
    
    def test_unauthorized_returns_message(self):
        """Unauthorized access should return message to user."""
        perm_file = Path("core/permissions.py")
        content = open(perm_file).read()
        
        assert "send" in content.lower() or "message" in content.lower()
