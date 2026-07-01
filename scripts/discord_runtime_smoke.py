#!/usr/bin/env python3
"""
WOS-M Discord Runtime Smoke Test
Tests that the bot can:
- Read env variables
- Initialize Discord client
- Connect to Gateway (if token available)
- Shutdown cleanly
© MANSOUR — WOS-M. All rights reserved.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_env() -> dict:
    """Check required environment variables."""
    required = ["DISCORD_BOT_TOKEN"]
    optional = ["DISCORD_APPLICATION_ID", "OWNER_DISCORD_ID", "TEST_GUILD_ID"]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"EXIT_CODE_2: Required env missing: {', '.join(missing)}")
        print("DISCORD_BOT_TOKEN missing; runtime QA not executed")
        return None
    
    env_values = {
        "DISCORD_BOT_TOKEN": "[SET]",
        "DISCORD_APPLICATION_ID": os.getenv("DISCORD_APPLICATION_ID", "[NOT SET]"),
        "OWNER_DISCORD_ID": os.getenv("OWNER_DISCORD_ID", "[NOT SET]"),
        "TEST_GUILD_ID": os.getenv("TEST_GUILD_ID", "[NOT SET]"),
    }
    
    return env_values


async def run_smoke_test(token: str):
    """Run the actual smoke test with a real token."""
    import discord
    from discord import Intents
    
    intents = Intents.default()
    intents.message_content = True
    intents.guilds = True
    
    client = discord.Client(intents=intents)
    
    connected = asyncio.Event()
    timeout_seconds = 30
    
    async def on_ready():
        logger.info(f"BOT_READY")
        logger.info(f"BOT_ID={client.user.id}")
        logger.info(f"GUILDS={len(client.guilds)}")
        connected.set()
    
    client.on_ready = on_ready
    
    logger.info("Starting Discord client...")
    asyncio.create_task(client.start(token))
    
    try:
        await asyncio.wait_for(connected.wait(), timeout=timeout_seconds)
        logger.info(f"Connected successfully within {timeout_seconds}s")
        
        await asyncio.sleep(5)
        
        await client.close()
        logger.info("Client closed cleanly")
        
        return True
        
    except asyncio.TimeoutError:
        logger.error(f"Failed to connect within {timeout_seconds}s")
        try:
            await client.close()
        except Exception:
            pass
        return False


def main():
    logger.info("=" * 60)
    logger.info("WOS-M Discord Runtime Smoke Test")
    logger.info("=" * 60)
    
    env_values = check_env()
    
    if env_values is None:
        logger.warning("Runtime QA skipped - no token available")
        sys.exit(2)
    
    logger.info("Environment variables loaded:")
    for key, value in env_values.items():
        if key == "DISCORD_BOT_TOKEN":
            logger.info(f"  {key}: [REDACTED]")
        else:
            logger.info(f"  {key}: {value}")
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    if token == "test_token_for_ci":
        logger.warning("Using test token - skipping actual connection")
        logger.info("Environment check PASSED (test mode)")
        sys.exit(0)
    
    try:
        result = asyncio.run(run_smoke_test(token))
        
        if result:
            logger.info("Discord Runtime Smoke Test PASSED")
            sys.exit(0)
        else:
            logger.error("Discord Runtime Smoke Test FAILED")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
