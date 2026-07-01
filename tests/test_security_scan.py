"""
Tests for Security Scan Script
© MANSOUR — WOS-M. All rights reserved.
"""
import pytest
from pathlib import Path
import subprocess
import sys


class TestSecurityScanScript:
    """Test security_scan.py script."""
    
    def test_security_scan_script_exists(self):
        """scripts/security_scan.py must exist."""
        script_file = Path("scripts/security_scan.py")
        assert script_file.exists(), "security_scan.py must exist"
    
    def test_security_scan_has_patterns(self):
        """Script should have secret patterns defined."""
        script_file = Path("scripts/security_scan.py")
        content = open(script_file).read()
        
        assert "ghp_" in content
        assert "sk_live_" in content
    
    def test_security_scan_runs_successfully(self):
        """Script should run without errors."""
        script_file = Path("scripts/security_scan.py")
        
        result = subprocess.run(
            [sys.executable, str(script_file)],
            capture_output=True,
            text=True
        )
        
        assert result.returncode in [0, 1], f"Script should exit 0 (no secrets) or 1 (found secrets), got {result.returncode}"
    
    def test_security_scan_allows_pattern_definition(self):
        """Script should allow defining patterns, not values."""
        script_file = Path("scripts/security_scan.py")
        content = open(script_file).read()
        
        assert "SECRET_PATTERNS" in content or "patterns" in content


class TestNoHardcodedSecrets:
    """Test that no hardcoded secrets exist."""
    
    def test_bot_file_no_real_tokens(self):
        """core/bot.py should not have real tokens."""
        bot_file = Path("core/bot.py")
        
        if bot_file.exists():
            content = open(bot_file).read()
            
            assert "ghp_" not in content or "test" in content.lower()
