"""
WOS-M Internationalization System
© MANSOUR — WOS-M. All rights reserved.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any

import aiosqlite


class I18n:
    """Internationalization manager for WOS-M."""
    
    _instance = None
    _locales: Dict[str, Dict[str, Any]] = {}
    _current_locale: str = "ar"
    _db: Optional[aiosqlite.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self, db: aiosqlite.Connection):
        """Initialize the i18n system."""
        self._db = db
        await self._load_locales()
        await self._load_current_locale()
    
    async def _load_locales(self):
        """Load all locale files."""
        locales_dir = Path(__file__).parent.parent / "locales"
        for locale_file in locales_dir.glob("*.json"):
            lang_code = locale_file.stem
            with open(locale_file, "r", encoding="utf-8") as f:
                self._locales[lang_code] = json.load(f)
    
    async def _load_current_locale(self):
        """Load the current locale from database."""
        if self._db:
            async with self._db.execute(
                "SELECT value FROM bot_settings WHERE key = 'language'"
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    self._current_locale = row[0]
    
    def get(self, key: str, locale: Optional[str] = None) -> str:
        """
        Get a translation by key.
        
        Args:
            key: Dot-separated key path (e.g., 'dashboard.title')
            locale: Optional locale code (defaults to current)
            
        Returns:
            Translated string or key if not found
        """
        lang = locale or self._current_locale
        locale_data = self._locales.get(lang, {})
        
        keys = key.split(".")
        value = locale_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return key
        
        return value if value is not None else key
    
    async def set_locale(self, locale: str) -> bool:
        """
        Set the current locale.
        
        Args:
            locale: Locale code (e.g., 'ar', 'en')
            
        Returns:
            True if successful, False otherwise
        """
        if locale not in self._locales:
            return False
        
        self._current_locale = locale
        
        if self._db:
            await self._db.execute(
                "INSERT OR REPLACE INTO bot_settings (key, value) VALUES ('language', ?)",
                (locale,)
            )
            await self._db.commit()
        
        return True
    
    @property
    def current_locale(self) -> str:
        """Get the current locale."""
        return self._current_locale
    
    @property
    def available_locales(self) -> list:
        """Get list of available locales."""
        return list(self._locales.keys())


i18n = I18n()
