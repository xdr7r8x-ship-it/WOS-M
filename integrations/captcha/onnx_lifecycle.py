"""
Lifecycle manager for ONNX/OCR model sessions.
Based on: https://github.com/whiteout-project/bot

Models are loaded on first acquire and unloaded after a grace period.
"""
from __future__ import annotations

import asyncio
import gc
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from typing import Any, Callable

logger = logging.getLogger(__name__)

DEFAULT_GRACE_SECONDS = 120
SWEEP_INTERVAL_SECONDS = 30

LOW_MEM_THRESHOLD_MB = 768


def _detect_memory_limit_mb() -> "int | None":
    """Detect container memory limit in MB."""
    for path in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            with open(path) as f:
                raw = f.read().strip()
        except OSError:
            continue
        if not raw or raw == "max":
            continue
        try:
            val = int(raw)
        except ValueError:
            continue
        if 0 < val < (1 << 62):
            return val // (1024 * 1024)
    return None


def _resolve_low_mem() -> "tuple[bool, int | None]":
    """Return (low_mem_mode, detected_limit_mb)."""
    limit = _detect_memory_limit_mb()
    override = os.environ.get("BOT_LOW_MEM", "").strip().lower()
    if override in ("1", "true", "yes", "on"):
        return True, limit
    if override in ("0", "false", "no", "off"):
        return False, limit
    return (limit is not None and limit <= LOW_MEM_THRESHOLD_MB), limit


LOW_MEM_MODE, MEM_LIMIT_MB = _resolve_low_mem()

if LOW_MEM_MODE:
    logger.info(f"Low-memory mode ON (limit={MEM_LIMIT_MB or '?'} MB)")
else:
    logger.info(f"Low-memory mode OFF (detected limit={MEM_LIMIT_MB or 'none'} MB)")


_REGISTRY: dict[str, "LazyOnnxModel"] = {}


async def _evict_other_idle_models(keep_name: str) -> None:
    """Evict non-pinned idle models."""
    drained = False
    for name, m in list(_REGISTRY.items()):
        if name == keep_name or m.pinned:
            continue
        async with m._lock:
            if m._model is not None and m._refcount == 0:
                m._model = None
                m._unload_pending_since = None
                logger.info(f"OCR model evicted: {name}")
                drained = True
    if drained:
        await _drain_and_collect()


async def _drain_and_collect() -> None:
    """Force GC collection."""
    try:
        await asyncio.to_thread(lambda: None)
    except Exception:
        pass
    gc.collect()


def get_or_create(
    name: str,
    display_name: str,
    factory: Callable[[], Any],
    grace_seconds: int = DEFAULT_GRACE_SECONDS,
    pinned: bool = False,
) -> "LazyOnnxModel":
    """Return the registered model with this name, creating it if missing."""
    if name in _REGISTRY:
        return _REGISTRY[name]
    return LazyOnnxModel(name, display_name, factory, grace_seconds, pinned)


class LazyOnnxModel:
    """Reference-counted lazy-loaded model wrapper."""

    def __init__(
        self,
        name: str,
        display_name: str,
        factory: Callable[[], Any],
        grace_seconds: int = DEFAULT_GRACE_SECONDS,
        pinned: bool = False,
    ):
        if name in _REGISTRY:
            raise ValueError(f"Duplicate ONNX model name: {name}")
        self.name = name
        self.display_name = display_name
        self.pinned = pinned
        self._factory = factory
        self._grace = timedelta(seconds=grace_seconds)
        self._model: Any = None
        self._refcount = 0
        self._last_used: datetime | None = None
        self._last_loaded: datetime | None = None
        self._unload_pending_since: datetime | None = None
        self._lock = asyncio.Lock()
        _REGISTRY[name] = self

    async def acquire(self):
        """Increment refcount. Loads the model if it isn't already."""
        async with self._lock:
            if self._model is None:
                logger.info(f"OCR model loading: {self.name}")
                self._model = await asyncio.to_thread(self._factory)
                self._last_loaded = datetime.now(timezone.utc)
            self._refcount += 1
            self._last_used = datetime.now(timezone.utc)
            self._unload_pending_since = None
            model = self._model
        if LOW_MEM_MODE and not self.pinned:
            await _evict_other_idle_models(self.name)
        return model

    async def release(self) -> None:
        """Decrement refcount."""
        async with self._lock:
            if self._refcount > 0:
                self._refcount -= 1
            self._last_used = datetime.now(timezone.utc)
            if self._refcount == 0:
                self._unload_pending_since = self._last_used

    @asynccontextmanager
    async def use(self):
        """Short-form auto acquire/release."""
        model = await self.acquire()
        try:
            yield model
        finally:
            await self.release()

    async def maybe_unload(self) -> bool:
        """Evict if idle past grace. Pinned models are never unloaded."""
        if self.pinned:
            return False
        async with self._lock:
            if self._model is None or self._refcount > 0 or self._unload_pending_since is None:
                return False
            elapsed = datetime.now(timezone.utc) - self._unload_pending_since
            if elapsed < self._grace:
                return False
            self._model = None
            self._unload_pending_since = None
            logger.info(f"OCR model unloaded: {self.name}")
        await _drain_and_collect()
        return True

    def status(self) -> dict:
        return {
            'name': self.name,
            'loaded': self._model is not None,
            'pinned': self.pinned,
            'refcount': self._refcount,
        }
