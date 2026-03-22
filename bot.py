#!/usr/bin/env python3
"""
Discord Persona Bot
A synthetic discourse generator for testing analysis tools
"""

import discord
from discord.ext import commands
import yaml
import os
import asyncio
import random
from datetime import datetime
import pytz
from dotenv import load_dotenv
import re
import argparse
import urllib.request
import xml.etree.ElementTree as ET
import json

load_dotenv()


class PersonaBot(commands.Bot):
    def __init__(self, persona_name, config, fast_mode=False):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True

        super().__init__(command_prefix='!', intents=intents)

        self.persona_name = persona_name
        self.config = config
        self.profile = config['profile']
        self.personality = config['personality']
        self.behavior = config['behavior']
        self.llm_config = config['llm_config']
        self.fast_mode = fast_mode

        if fast_mode:
            self.behavior['response_delay_min'] = 20
            self.behavior['response_delay_max'] = 40
            self.behavior['bot_reply_delay_min'] = 10
            self.behavior['bot_reply_delay_max'] = 20
            self.behavior['reply_probability'] = 1.0
            self.behavior['initiation_interval_min'] = 30
            self.behavior['initiation_interval_max'] = 60
            self.log("⚡ FAST MODE: short delays, always replies, frequent initiation")

        self.tz = pytz.timezone(self.profile['timezone'])
        self.context = []
        self._was_active = None

    def log(self, msg):
        """Prefixed log so multi-bot output is readable"""
        print(f"[{self.profile['name']}] {msg}")

    async def on_ready(self):
        self.log(f"online as {self.user}")
        self.log(f"Style: {self.personality.get('style', 'default')}")

        # Load recent channel history
        for guild in self.guilds:
            for channel in guild.text_channels:
                try:
                    messages = []
                    async for msg in channel.history(limit=20):
                        if msg.author != self.user:
                            messages.append({
                                'author': msg.author.name,
                                'content': msg.content,
                                'timestamp': msg.created_at
                            })
                    self.context.extend(reversed(messages))
                    if messages:
                        self.log(f"Loaded {len(messages)} messages from #{channel.name}")
                except Exception:
                    pass
        self.context = self.context[-20:]

        # Start autonomous initiation loop
        asyncio.create_task(self.initiation_loop())

    async def on_message(self, message):
        if message.author == self.user:
            return
        if self.fast_mode and message.author.bot:
            return

        # Update context
        self.context.append({
            'author': message.author.name,
            'content': message.content,
            'timestamp': message.created_at
        })
        if len(self.context) > 20:
            self.context.pop(0)

        if await self.should_respond(message):
            delay = self.calculate_response_delay(is_bot_message=message.author.bot)
            self.log(f"Contemplating for {delay:.0f}s...")
            await asyncio.sleep(delay)

            response = await self.generate_response(message.author.name, message.content)
            response = self.add_typos(response)
            response = self.add_emojis(response)

            async with message.channel.typing():
                await asyncio.sleep(random.uniform(1, 3))
                await message.channel.send(response)
                self.log(f"Replied to {message.author.name}")

    async def initiation_loop(self):
        """Proactively post to the channel on a schedule, with sleep/wake awareness"""
        await asyncio.sleep(random.uniform(30, 120))

        while True:
            interval = random.uniform(
                self.behavior.get('initiation_interval_min', 900),
                self.behavior.get('initiation_interval_max', 3600)
            )
            await asyncio.sleep(interval)

            now_active = True if self.fast_mode else self.is_active_hour()

            # Detect wake-up transition
            if self._was_active is False and now_active:
                self._was_active = now_active
                asyncio.create_task(self._wake_up_burst())
                continue

            self._was_active = now_active

            if not now_active:
                continue

            # Find the target channel
            channel_name = self.behavior.get('initiation_channel', 'general')
            channel = None
            for guild in self.guilds:
                for ch in guild.text_channels:
                    if ch.name == channel_name:
                        channel = ch
                        break

            if not channel:
                continue

            starters = self.config.get('conversation_starters', [])
            if not starters:
                continue

            # ~35% chance: react to a real news headline instead of a starter
            raw_prompt = None
            starter = None
            if random.random() < 0.35:
                headlines = self.fetch_news()
                if headlines:
                    headline = random.choice(headlines)
                    raw_prompt = (
                        f"Here's a real news headline: \"{headline}\"\n\n"
                        f"As {self.profile['name']}, post a short reaction to this news. "
                        f"Stay completely in character. 1-2 sentences. Don't just quote the headline."
                    )

            if raw_prompt is None:
                starter = random.choice(starters)

            response = await self.generate_response(None, None, starter=starter, raw_prompt=raw_prompt)
            response = self.add_typos(response)
            response = self.add_emojis(response)

            async with channel.typing():
                await asyncio.sleep(random.uniform(1, 3))
                await channel.send(response)
                self.log(f"Initiated in #{channel_name}")

    async def _wake_up_burst(self):
        """Post a catch-up reaction when coming online after being inactive"""
        channel_name = self.behavior.get('initiation_channel', 'general')
        channel = None
        for guild in self.guilds:
            for ch in guild.text_channels:
                if ch.name == channel_name:
                    channel = ch
                    break
        if not channel:
            return

        recent = []
        async for msg in channel.history(limit=10):
            if msg.author != self.user:
                recent.append(f"{msg.author.name}: {msg.content}")
        recent.reverse()

        if not recent:
            return

        missed = "\n".join(recent[-6:])
        raw_prompt = (
            f"You just came online after being away. Here's what you missed:\n{missed}\n\n"
            f"As {self.profile['name']}, react to the most interesting thing above. "
            f"1-2 sentences max. Stay in character."
        )
        response = await self.generate_response(None, None, raw_prompt=raw_prompt)
        response = self.add_typos(response)
        response = self.add_emojis(response)

        async with channel.typing():
            await asyncio.sleep(random.uniform(1, 3))
            await channel.send(response)
            self.log("Wake-up burst posted")

    def fetch_news(self, max_items=10):
        """Fetch BBC RSS headlines, return list of title strings"""
        try:
            req = urllib.request.Request(
                'https://feeds.bbci.co.uk/news/rss.xml',
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                root = ET.fromstring(resp.read())
            titles = []
            for item in root.findall('./channel/item'):
                title = item.findtext('title')
                if title:
                    titles.append(title.strip())
                if len(titles) >= max_items:
                    break
            return titles
        except Exception as e:
            self.log(f"News fetch error: {e}")
            return []

    def is_active_hour(self):
        """Check active hours, handling overnight ranges like [20, 2]"""
        hour = datetime.now(self.tz).hour
        start, end = self.behavior['active_hours']
        if start <= end:
            return start <= hour <= end
        else:  # overnight wrap e.g. [20, 2]
            return hour >= start or hour <= end

    async def should_respond(self, message):
        if not self.fast_mode and not self.is_active_hour():
            return False
        return random.random() < self.behavior['reply_probability']

    def calculate_response_delay(self, is_bot_message=False):
        if is_bot_message:
            min_d = self.behavior.get('bot_reply_delay_min', 30)
            max_d = self.behavior.get('bot_reply_delay_max', 120)
        else:
            min_d = self.behavior['response_delay_min']
            max_d = self.behavior['response_delay_max']
        return random.uniform(min_d, max_d)

    async def generate_response(self, author_name, content, starter=None, raw_prompt=None):
        """Generate a response (or initiation) via Ollama"""

        context_str = "\n".join([
            f"{msg['author']}: {msg['content']}"
            for msg in self.context[-10:]
        ])

        other_bots = self.config.get('other_bots', [])
        others_str = ""
        if other_bots:
            names = [b['name'] for b in other_bots]
            others_str = f"\n\nOthers in this server: {', '.join(names)}. @ them by name when challenging or addressing them directly."

        system = self.llm_config['system_prompt'].strip() + others_str

        if raw_prompt:
            prompt = raw_prompt
        elif starter:
            prompt = f"""You want to post something to start a conversation. Your seed thought: "{starter}"

Recent channel context:
{context_str}

Post a message as {self.profile['name']}. Stay in character. 1-2 sentences maximum."""
        else:
            prompt = f"""Recent conversation:
{context_str}

{author_name}: {content}

Respond as {self.profile['name']}. Stay in character. 1-2 sentences maximum."""

        try:
            payload = json.dumps({
                'model': self.llm_config['model'],
                'system': system,
                'prompt': prompt,
                'stream': False,
                'options': {'temperature': self.llm_config.get('temperature', 0.8)}
            }).encode()

            req = urllib.request.Request(
                'http://localhost:11434/api/generate',
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=1200) as resp:
                data = json.loads(resp.read())
                response = data.get('response', '').strip()

            if not response:
                self.log("Ollama returned empty response")
                return self.get_fallback_response()

            return response

        except Exception as e:
            self.log(f"LLM error: {e}")
            return self.get_fallback_response()

    def get_fallback_response(self):
        responses = self.personality.get('core_beliefs', [
            "Interesting.",
            "I have thoughts on this.",
            "Tell me more."
        ])
        return random.choice(responses)

    def add_typos(self, text):
        if random.random() > self.behavior.get('typo_rate', 0.02):
            return text
        words = text.split()
        if len(words) > 3:
            word_idx = random.randint(0, len(words) - 1)
            word = words[word_idx]
            if len(word) > 3:
                char_idx = random.randint(1, len(word) - 2)
                words[word_idx] = word[:char_idx] + word[char_idx] + word[char_idx:]
                return ' '.join(words)
        return text

    def add_emojis(self, text):
        if random.random() > self.behavior.get('emoji_frequency', 0.2):
            return text
        emojis = self.personality.get('emojis', ['🤔', '✨', '👀'])
        return text + ' ' + random.choice(emojis)


def load_single_config(config_file='philosophers.yaml'):
    """Load a single enabled bot from config (legacy single-bot mode)"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', config_file)

    with open(config_path, 'r') as f:
        all_configs = yaml.safe_load(f)

    for name, config in all_configs.items():
        if config.get('enabled', False):
            token_env = config.get('discord_token_env', 'DISCORD_TOKEN')
            config['discord_token'] = os.getenv(token_env)
            if not config['discord_token']:
                raise ValueError(f"Token env var '{token_env}' not found in .env")
            return name, config

    raise ValueError(f"No bot enabled in {config_file}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fast', action='store_true', help='Fast mode: minimal delays, always replies')
    parser.add_argument('--config', default='philosophers.yaml', help='Config file in config/ directory')
    args = parser.parse_args()

    print("=" * 60)
    print("Discord Persona Bot - Synthetic Discourse Generator")
    print("=" * 60)

    try:
        name, config = load_single_config(args.config)
    except Exception as e:
        print(f"Error: {e}")
        return

    bot = PersonaBot(name, config, fast_mode=args.fast)

    try:
        bot.run(config['discord_token'])
    except discord.LoginFailure:
        print("Invalid Discord token. Check your .env file.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
