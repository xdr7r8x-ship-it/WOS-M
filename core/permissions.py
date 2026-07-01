"""
WOS-M Permissions System
© MANSOUR — WOS-M. All rights reserved.
"""
from enum import Enum
from typing import Optional, List
import aiosqlite

from core.database import db


class PermissionLevel(Enum):
    """Permission levels hierarchy."""
    OWNER = 1
    GLOBAL_ADMIN = 2
    SERVER_ADMIN = 3
    ADMIN = 3  # Alias for SERVER_ADMIN
    ALLIANCE_ADMIN = 4
    MEMBER = 5

    @classmethod
    def from_string(cls, value: str) -> "PermissionLevel":
        """Convert string to PermissionLevel."""
        mapping = {
            "owner": cls.OWNER,
            "global_admin": cls.GLOBAL_ADMIN,
            "server_admin": cls.SERVER_ADMIN,
            "admin": cls.SERVER_ADMIN,
            "alliance_admin": cls.ALLIANCE_ADMIN,
            "member": cls.MEMBER,
        }
        return mapping.get(value.lower(), cls.MEMBER)

    def __ge__(self, other: "PermissionLevel") -> bool:
        """Check if permission level is >= another."""
        return self.value <= other.value
    
    def __gt__(self, other: "PermissionLevel") -> bool:
        """Check if permission level is > another."""
        return self.value < other.value
    
    def __le__(self, other: "PermissionLevel") -> bool:
        """Check if permission level is <= another."""
        return self.value >= other.value
    
    def __lt__(self, other: "PermissionLevel") -> bool:
        """Check if permission level is < another."""
        return self.value > other.value


class PermissionGuard:
    """Permission guard for WOS-M."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def is_owner(self, user_id: str) -> bool:
        """Check if user is the bot owner."""
        owner_id = self.bot.owner_id
        return str(user_id) == str(owner_id)
    
    async def has_permission(
        self,
        user_id: str,
        required_level: PermissionLevel,
        guild_id: Optional[str] = None,
        alliance_id: Optional[int] = None
    ) -> bool:
        """
        Check if user has the required permission level.
        
        Args:
            user_id: Discord user ID
            required_level: Required permission level
            guild_id: Optional guild ID
            alliance_id: Optional alliance ID
            
        Returns:
            True if user has permission, False otherwise
        """
        # Owner always has permission
        if await self.is_owner(user_id):
            return True
        
        user_level = await self.get_user_level(user_id, guild_id, alliance_id)
        return user_level >= required_level
    
    async def get_user_level(
        self,
        user_id: str,
        guild_id: Optional[str] = None,
        alliance_id: Optional[int] = None
    ) -> PermissionLevel:
        """Get the highest permission level for a user."""
        # Check admins table first
        row = await db.fetchone(
            "SELECT role FROM admins WHERE discord_id = ?",
            (str(user_id),)
        )
        
        if row:
            return PermissionLevel.from_string(row["role"])
        
        # Check permissions table
        query = "SELECT role FROM permissions WHERE discord_id = ?"
        params = [str(user_id)]
        
        if guild_id:
            query += " AND (guild_id = ? OR guild_id IS NULL)"
            params.append(str(guild_id))
        
        row = await db.fetchone(query, tuple(params))
        
        if row:
            return PermissionLevel.from_string(row["role"])
        
        return PermissionLevel.MEMBER
    
    async def add_admin(
        self,
        user_id: str,
        role: str,
        added_by: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Add an admin."""
        if role == "owner":
            return False  # Cannot add owner this way
        
        await db.execute(
            """INSERT OR REPLACE INTO admins 
               (discord_id, discord_name, role, added_by) 
               VALUES (?, ?, ?, ?)""",
            (str(user_id), user_name, role, str(added_by))
        )
        await db.commit()
        return True
    
    async def remove_admin(self, user_id: str) -> bool:
        """Remove an admin."""
        row = await db.fetchone(
            "SELECT role FROM admins WHERE discord_id = ?",
            (str(user_id),)
        )
        
        if row and row["role"] == "owner":
            return False  # Cannot remove owner
        
        await db.execute(
            "DELETE FROM admins WHERE discord_id = ?",
            (str(user_id),)
        )
        await db.commit()
        return True
    
    async def get_admins(self) -> List[aiosqlite.Row]:
        """Get all admins."""
        return await db.fetchall(
            "SELECT * FROM admins ORDER BY role, added_at"
        )
    
    async def set_owner(self, user_id: str, user_name: Optional[str] = None) -> bool:
        """Transfer ownership to a new user."""
        # Remove old owner
        await db.execute(
            "UPDATE admins SET role = 'global_admin' WHERE role = 'owner'"
        )
        
        # Set new owner
        await db.execute(
            """INSERT OR REPLACE INTO admins 
               (discord_id, discord_name, role) 
               VALUES (?, ?, 'owner')""",
            (str(user_id), user_name)
        )
        await db.commit()
        
        # Update bot settings
        await db.execute(
            "INSERT OR REPLACE INTO bot_settings (key, value) VALUES ('owner_id', ?)",
            (str(user_id),)
        )
        await db.commit()
        
        return True
    
    async def get_permission_audit_log(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[aiosqlite.Row]:
        """Get permission-related audit logs."""
        return await db.fetchall(
            """SELECT * FROM audit_logs 
               WHERE category = 'permissions' 
               ORDER BY timestamp DESC 
               LIMIT ? OFFSET ?""",
            (limit, offset)
        )


def require_permission(level: PermissionLevel):
    """Decorator to require a specific permission level."""
    def decorator(func):
        async def wrapper(self, interaction, *args, **kwargs):
            guard = PermissionGuard(self.bot)
            user_id = str(interaction.user.id)
            
            if not await guard.has_permission(user_id, level):
                from core.i18n import i18n
                await interaction.response.send_message(
                    i18n.get("messages.no_permission"),
                    ephemeral=True
                )
                return False
            
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator
