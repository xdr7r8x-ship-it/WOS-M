#!/usr/bin/env python3
"""
WOS-M Discord Runtime Smoke Test
Tests that the bot can:
- Read env variables
- Initialize Discord client
- Connect to Gateway (if token available)
- Shutdown cleanly

CRITICAL: This test requires a REAL Discord bot token.
test_token_for_ci is NOT allowed and will cause FAILURE.

Exit codes:
- 0: Success with real Gateway connection
- 1: Failure (test token used or connection failed)
- 2: Missing required environment variables

© MANSOUR — WOS-M. All rights reserved.
"""
import os
import sys
import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_env() -> dict:
    """Check required environment variables."""
    required = ["DISCORD_BOT_TOKEN"]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Required env missing: {', '.join(missing)}")
        sys.exit(2)
    
    token = os.getenv("DISCORD_BOT_TOKEN", "")
    
    # CRITICAL: Reject test tokens - Final Quality Gate requires real connection
    if token == "test_token_for_ci":
        logger.error("test_token_for_ci is not allowed for Final Quality Gate")
        logger.error("Real Discord bot token required for Discord Runtime QA Live")
        sys.exit(1)
    
    env_values = {
        "DISCORD_BOT_TOKEN": "[SET - REDACTED]",
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
        print(f"BOT_READY")
        print(f"BOT_ID={client.user.id}")
        print(f"GUILDS={len(client.guilds)}")
        logger.info("Gateway connection established")
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
    
    logger.info("Environment variables loaded:")
    for key, value in env_values.items():
        logger.info(f"  {key}: {value}")
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    
    try:
        result = asyncio.run(run_smoke_test(token))
        
        if result:
            logger.info("Discord Runtime Smoke Test PASSED")
            logger.info("Gateway connection verified")
            sys.exit(0)
        else:
            logger.error("Discord Runtime Smoke Test FAILED")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
