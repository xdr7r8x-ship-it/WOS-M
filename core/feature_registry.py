"""
WOS-M Feature Registry System
© MANSOUR — WOS-M. All rights reserved.
"""
import json
from typing import Optional, Dict, Any, List
import logging

from core.database import db

logger = logging.getLogger(__name__)


class FeatureManifest:
    """Feature manifest structure."""
    
    def __init__(
        self,
        key: str,
        name_ar: str,
        name_en: str,
        description_ar: str = "",
        description_en: str = "",
        icon: str = "⚙️",
        enabled: bool = True,
        required_permission: str = "member",
        entry_button: bool = True,
        handler: str = ""
    ):
        self.key = key
        self.name = {"ar": name_ar, "en": name_en}
        self.description = {"ar": description_ar, "en": description_en}
        self.icon = icon
        self.enabled = enabled
        self.required_permission = required_permission
        self.entry_button = entry_button
        self.handler = handler
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "enabled": self.enabled,
            "required_permission": self.required_permission,
            "entry_button": self.entry_button,
            "handler": self.handler
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureManifest":
        """Create from dictionary."""
        return cls(
            key=data.get("key", ""),
            name_ar=data.get("name", {}).get("ar", ""),
            name_en=data.get("name", {}).get("en", ""),
            description_ar=data.get("description", {}).get("ar", ""),
            description_en=data.get("description", {}).get("en", ""),
            icon=data.get("icon", "⚙️"),
            enabled=data.get("enabled", True),
            required_permission=data.get("required_permission", "member"),
            entry_button=data.get("entry_button", True),
            handler=data.get("handler", "")
        )
    
    @classmethod
    def from_db_row(cls, row) -> "FeatureManifest":
        """Create from database row."""
        return cls(
            key=row["feature_key"],
            name_ar=row["name_ar"],
            name_en=row["name_en"],
            description_ar=row.get("description_ar", ""),
            description_en=row.get("description_en", ""),
            icon=row.get("icon", "⚙️"),
            enabled=bool(row["is_enabled"]),
            required_permission=row.get("required_permission", "member"),
            entry_button=bool(row.get("entry_button", True)),
            handler=row.get("handler_path", "")
        )


class FeatureRegistry:
    """Centralized feature registry system."""
    
    DEFAULT_FEATURES: List[Dict[str, Any]] = [
        {
            "key": "alliances",
            "name": {"ar": "التحالفات", "en": "Alliances"},
            "description": {"ar": "إدارة التحالفات", "en": "Alliance management"},
            "icon": "🏰",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.alliances.views"
        },
        {
            "key": "players",
            "name": {"ar": "اللاعبين", "en": "Players"},
            "description": {"ar": "إدارة اللاعبين", "en": "Player management"},
            "icon": "👥",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.players.views"
        },
        {
            "key": "gift_codes",
            "name": {"ar": "استرداد الأكواد", "en": "Gift Codes"},
            "description": {"ar": "نظام استرداد أكواد الهدايا", "en": "Gift code redemption system"},
            "icon": "🎁",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.gift_codes.views"
        },
        {
            "key": "events",
            "name": {"ar": "الأحداث", "en": "Events"},
            "description": {"ar": "إدارة الأحداث", "en": "Event management"},
            "icon": "📅",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.events.views"
        },
        {
            "key": "attendance",
            "name": {"ar": "الحضور", "en": "Attendance"},
            "description": {"ar": "إدارة الحضور", "en": "Attendance management"},
            "icon": "✅",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.attendance.views"
        },
        {
            "key": "bear_tracking",
            "name": {"ar": "تتبع الدب", "en": "Bear Tracking"},
            "description": {"ar": "تتبع أحداث الدب", "en": "Bear event tracking"},
            "icon": "🐻",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.bear_tracking.views"
        },
        {
            "key": "ministers",
            "name": {"ar": "الوزراء", "en": "Ministers"},
            "description": {"ar": "إدارة الوزراء", "en": "Minister management"},
            "icon": "👔",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.ministers.views"
        },
        {
            "key": "notifications",
            "name": {"ar": "التنبيهات", "en": "Notifications"},
            "description": {"ar": "إدارة التنبيهات", "en": "Notification management"},
            "icon": "🔔",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.notifications.views"
        },
        {
            "key": "themes",
            "name": {"ar": "الثيم والهوية", "en": "Theme & Branding"},
            "description": {"ar": "إدارة الثيم والهوية البصرية", "en": "Theme and branding management"},
            "icon": "🎨",
            "enabled": True,
            "required_permission": "member",
            "entry_button": True,
            "handler": "modules.themes.views"
        },
        {
            "key": "permissions",
            "name": {"ar": "الصلاحيات", "en": "Permissions"},
            "description": {"ar": "إدارة الصلاحيات", "en": "Permission management"},
            "icon": "🔐",
            "enabled": True,
            "required_permission": "alliance_admin",
            "entry_button": True,
            "handler": "modules.maintenance.views"
        },
        {
            "key": "maintenance",
            "name": {"ar": "الصيانة", "en": "Maintenance"},
            "description": {"ar": "أدوات الصيانة", "en": "Maintenance tools"},
            "icon": "🔧",
            "enabled": True,
            "required_permission": "global_admin",
            "entry_button": True,
            "handler": "modules.maintenance.views"
        },
        {
            "key": "owner_panel",
            "name": {"ar": "لوحة المالك", "en": "Owner Panel"},
            "description": {"ar": "لوحة تحكم المالك", "en": "Owner control panel"},
            "icon": "👑",
            "enabled": True,
            "required_permission": "owner",
            "entry_button": True,
            "handler": "modules.owner_panel.views"
        }
    ]
    
    def __init__(self, bot):
        self.bot = bot
        self._features: Dict[str, FeatureManifest] = {}
    
    async def load_features(self):
        """Load features from database."""
        rows = await db.fetchall("SELECT * FROM feature_registry")
        
        if not rows:
            # Initialize with defaults
            for feature in self.DEFAULT_FEATURES:
                await self.add_feature(FeatureManifest.from_dict(feature))
        else:
            for row in rows:
                manifest = FeatureManifest.from_db_row(row)
                self._features[manifest.key] = manifest
        
        logger.info(f"Loaded {len(self._features)} features")
    
    async def add_feature(self, manifest: FeatureManifest) -> bool:
        """Add a new feature to the registry."""
        await db.execute(
            """INSERT OR REPLACE INTO feature_registry 
               (feature_key, name_ar, name_en, description_ar, description_en, 
                icon, is_enabled, required_permission, entry_button, handler_path) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (manifest.key, manifest.name["ar"], manifest.name["en"],
             manifest.description["ar"], manifest.description["en"],
             manifest.icon, manifest.enabled, manifest.required_permission,
             manifest.entry_button, manifest.handler)
        )
        await db.commit()
        
        self._features[manifest.key] = manifest
        logger.info(f"Added feature: {manifest.key}")
        return True
    
    async def update_feature(self, key: str, updates: Dict[str, Any]) -> bool:
        """Update a feature's properties."""
        if key not in self._features:
            return False
        
        feature = self._features[key]
        
        for field, value in updates.items():
            if field == "name":
                if "ar" in value:
                    feature.name["ar"] = value["ar"]
                if "en" in value:
                    feature.name["en"] = value["en"]
            elif field == "description":
                if "ar" in value:
                    feature.description["ar"] = value["ar"]
                if "en" in value:
                    feature.description["en"] = value["en"]
            elif hasattr(feature, field):
                setattr(feature, field, value)
        
        await self.add_feature(feature)
        return True
    
    async def remove_feature(self, key: str) -> bool:
        """Remove a feature from the registry."""
        if key not in self._features:
            return False
        
        await db.execute(
            "DELETE FROM feature_registry WHERE feature_key = ?",
            (key,)
        )
        await db.commit()
        
        del self._features[key]
        logger.info(f"Removed feature: {key}")
        return True
    
    async def enable_feature(self, key: str) -> bool:
        """Enable a feature."""
        return await self.update_feature(key, {"enabled": True})
    
    async def disable_feature(self, key: str) -> bool:
        """Disable a feature."""
        return await self.update_feature(key, {"enabled": False})
    
    def get_feature(self, key: str) -> Optional[FeatureManifest]:
        """Get a feature by key."""
        return self._features.get(key)
    
    def get_all_features(self) -> List[FeatureManifest]:
        """Get all registered features."""
        return list(self._features.values())
    
    def get_enabled_features(self) -> List[FeatureManifest]:
        """Get all enabled features."""
        return [f for f in self._features.values() if f.enabled]
    
    def get_features_by_permission(self, permission: str) -> List[FeatureManifest]:
        """Get features that require a specific permission."""
        return [f for f in self._features.values() if f.required_permission == permission]
    
    def is_feature_enabled(self, key: str) -> bool:
        """Check if a feature is enabled."""
        feature = self._features.get(key)
        return feature.enabled if feature else False


feature_registry: Optional[FeatureRegistry] = None
