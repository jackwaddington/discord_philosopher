#!/usr/bin/env python3
"""
Multi-bot launcher - runs all enabled personas in a single process.

Usage:
  python run.py                  # run all enabled bots from personas.yaml
  python run.py --fast           # fast mode (short delays, frequent posts)
  python run.py don techbro      # run only specific personas
  python run.py --config philosophers.yaml  # use a different config file
"""

import asyncio
import yaml
import os
import sys
import argparse
from dotenv import load_dotenv
from bot import PersonaBot

load_dotenv()


def load_configs(config_file, persona_filter=None):
    config_path = os.path.join(os.path.dirname(__file__), 'config', config_file)

    with open(config_path, 'r') as f:
        all_configs = yaml.safe_load(f)

    bots = []
    for name, config in all_configs.items():
        if persona_filter and name not in persona_filter:
            continue
        if not config.get('enabled', False):
            continue

        token_env = config.get('discord_token_env', 'DISCORD_TOKEN')
        token = os.getenv(token_env)
        if not token:
            print(f"  ⚠️  No token for '{name}' (expected env var: {token_env}) - skipping")
            continue

        config['discord_token'] = token
        bots.append((name, config, token))

    return bots


async def main():
    parser = argparse.ArgumentParser(description='Run Discord persona bots')
    parser.add_argument('personas', nargs='*', help='Specific persona names to run (default: all enabled)')
    parser.add_argument('--fast', action='store_true', help='Fast mode: short delays, always replies')
    parser.add_argument('--config', default='personas.yaml', help='Config file in config/ directory')
    args = parser.parse_args()

    print("=" * 60)
    print("Discord Synthetic Discourse - Multi-Bot Launcher")
    print("=" * 60)

    persona_filter = set(args.personas) if args.personas else None
    bot_configs = load_configs(args.config, persona_filter)

    if not bot_configs:
        print("No bots to run. Check your config file and .env tokens.")
        return

    print(f"\nStarting {len(bot_configs)} bot(s):")
    for name, config, _ in bot_configs:
        mode = "⚡ FAST" if args.fast else "normal"
        print(f"  • {config['profile']['name']} ({name}) [{mode}]")
    print()

    bots = [
        PersonaBot(name, config, fast_mode=args.fast)
        for name, config, _ in bot_configs
    ]

    try:
        await asyncio.gather(*[
            bot.start(token)
            for bot, (_, _, token) in zip(bots, bot_configs)
        ])
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await asyncio.gather(*[bot.close() for bot in bots], return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())
