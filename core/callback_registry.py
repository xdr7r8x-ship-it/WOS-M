"""
WOS-M Callback Registry
Centralized routing for all button and select interactions.
© MANSOUR — WOS-M. All rights reserved.
"""
import logging
from typing import Dict, Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CallbackRegistry:
    """Central registry for all interaction callbacks."""
    
    _instance = None
    _callbacks: Dict[str, Callable] = {}
    _modules: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._callbacks = {}
            cls._modules = {}
        return cls._instance
    
    def register(self, custom_id: str, handler: Callable, module: str = "core"):
        """Register a callback handler for a custom_id."""
        self._callbacks[custom_id] = handler
        logger.debug(f"Registered callback: {custom_id} -> {handler.__name__} ({module})")
    
    def register_module(self, module_name: str, module_callbacks: Dict[str, Callable]):
        """Register all callbacks from a module."""
        for custom_id, handler in module_callbacks.items():
            self.register(custom_id, handler, module_name)
    
    def get_handler(self, custom_id: str) -> Optional[Callable]:
        """Get handler for a custom_id."""
        return self._callbacks.get(custom_id)
    
    def is_registered(self, custom_id: str) -> bool:
        """Check if a custom_id has a handler."""
        return custom_id in self._callbacks
    
    def get_all_custom_ids(self) -> set:
        """Get all registered custom_ids."""
        return set(self._callbacks.keys())
    
    def get_stats(self) -> Dict[str, int]:
        """Get registry statistics."""
        return {
            "total_callbacks": len(self._callbacks),
            "total_modules": len(self._modules)
        }


# Global registry instance
callback_registry = CallbackRegistry()


def register_callback(custom_id: str, module: str = "core"):
    """Decorator to register a callback handler."""
    def decorator(func: Callable) -> Callable:
        callback_registry.register(custom_id, func, module)
        return func
    return decorator


def safe_callback_handler(func: Callable) -> Callable:
    """Decorator for safe callback handling with proper error messages."""
    @wraps(func)
    async def wrapper(self, interaction, *args, **kwargs):
        try:
            return await func(self, interaction, *args, **kwargs)
        except Exception as e:
            logger.error(f"Callback error in {func.__name__}: {e}", exc_info=True)
            try:
                await interaction.response.send_message(
                    "❌ حدث خطأ أثناء تنفيذ العملية. تم تسجيل التفاصيل.",
                    ephemeral=True
                )
            except:
                pass
            return None
    return wrapper