#!/usr/bin/env python3
"""
Discord Philosopher Bot
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

# Load environment
load_dotenv()

class PhilosopherBot(commands.Bot):
    def __init__(self, config, fast_mode=False):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        
        super().__init__(command_prefix='!', intents=intents)

        self.config = config
        self.profile = config['profile']
        self.personality = config['personality']
        self.behavior = config['behavior']
        self.llm_config = config['llm_config']
        self.fast_mode = fast_mode

        if fast_mode:
            self.behavior['response_delay_min'] = 30
            self.behavior['response_delay_max'] = 60
            self.behavior['reply_probability'] = 1.0
            print("⚡ FAST MODE: delays=30-60s, always replies")
        
        # Stalker mode
        self.is_stalker = 'stalker_config' in config
        self.stalker_target = config.get('stalker_config', {}).get('target_username')
        self.stalker_focus = config.get('stalker_config', {}).get('focus_probability', 0.75)
        
        # Timezone awareness
        self.tz = pytz.timezone(self.profile['timezone'])
        
        # Conversation memory (last 20 messages)
        self.context = []
        
    async def on_ready(self):
        print(f'🎭 {self.profile["name"]} has entered the discourse')
        print(f'   Location: {self.profile["location"]}')
        print(f'   Philosophy: {self.profile["philosophy"]}')
        if self.is_stalker:
            print(f'   👀 Stalker mode: Watching {self.stalker_target}')
        print()

        # Load recent history from all accessible channels
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
                    # History comes newest-first, reverse for chronological order
                    self.context.extend(reversed(messages))
                    if messages:
                        print(f'   📜 Loaded {len(messages)} messages from #{channel.name}')
                except Exception:
                    pass
        # Keep only last 20
        self.context = self.context[-20:]
        
    async def on_message(self, message):
        # Ignore own messages
        if message.author == self.user:
            return
        # In fast mode, ignore other bots to prevent infinite loops
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
        
        # Check if we should respond
        should_respond = await self.should_respond(message)
        
        if should_respond:
            # Wait realistic amount of time
            delay = await self.calculate_response_delay()
            print(f"   💭 Contemplating for {delay/60:.1f} minutes...")
            await asyncio.sleep(delay)
            
            # Generate response
            response = await self.generate_response(message)
            
            # Add realistic elements
            response = self.add_typos(response)
            response = self.add_emojis(response)
            
            # Send
            async with message.channel.typing():
                await asyncio.sleep(random.uniform(2, 5))  # "typing" delay
                await message.channel.send(response)
                print(f"   💬 Responded to {message.author.name}")
    
    async def should_respond(self, message):
        """Decide if bot should respond to this message"""

        # Don't respond if not in active hours (skipped in fast mode)
        if not self.fast_mode:
            local_hour = datetime.now(self.tz).hour
            if not (self.behavior['active_hours'][0] <= local_hour <= self.behavior['active_hours'][1]):
                return False
        
        # Stalker mode: prioritize target
        if self.is_stalker and message.author.name == self.stalker_target:
            return random.random() < self.stalker_focus
        
        # Regular probability
        return random.random() < self.behavior['reply_probability']
    
    async def calculate_response_delay(self):
        """Calculate realistic response delay based on config"""
        min_delay = self.behavior['response_delay_min']
        max_delay = self.behavior['response_delay_max']
        return random.uniform(min_delay, max_delay)
    
    async def generate_response(self, message):
        """Generate philosophical response using local LLM"""
        
        # Build context for LLM
        context_str = "\n".join([
            f"{msg['author']}: {msg['content']}" 
            for msg in self.context[-10:]  # Last 10 messages
        ])
        
        # Build prompt
        prompt = f"""Recent conversation:
{context_str}

{message.author.name}: {message.content}

Respond as {self.profile['name']}, staying true to your philosophical character.
Keep it conversational (2-4 sentences usually). Be authentic to your philosophy.
"""

        # Call Ollama via HTTP API
        try:
            import urllib.request
            import json

            payload = json.dumps({
                'model': self.llm_config['model'],
                'system': self.llm_config['system_prompt'],
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
                print("   ⚠️ Ollama returned empty response")
                response = self.get_fallback_response()

            return response

        except Exception as e:
            print(f"   ⚠️ LLM error: {e}")
            return self.get_fallback_response()
    
    def get_fallback_response(self):
        """Simple fallback if LLM fails"""
        responses = self.personality.get('core_beliefs', [
            "Interesting perspective.",
            "I must contemplate this further.",
            "Tell me more."
        ])
        return random.choice(responses)
    
    def add_typos(self, text):
        """Occasionally add realistic typos"""
        if random.random() > self.behavior['typo_rate']:
            return text
            
        # Simple typo: duplicate a letter
        words = text.split()
        if len(words) > 3:
            word_idx = random.randint(0, len(words)-1)
            word = words[word_idx]
            if len(word) > 3:
                char_idx = random.randint(1, len(word)-2)
                words[word_idx] = word[:char_idx] + word[char_idx] + word[char_idx:]
                return ' '.join(words)
        
        return text
    
    def add_emojis(self, text):
        """Occasionally add emojis based on personality"""
        if random.random() > self.behavior['emoji_frequency']:
            return text
        
        # Get emojis from special behaviors or use defaults
        emojis = ['🤔', '📚', '✨']
        
        # Try to extract emojis from special behaviors
        for behavior in self.config.get('special_behaviors', []):
            found_emojis = re.findall(r'[\U0001F300-\U0001F9FF]', behavior)
            if found_emojis:
                emojis.extend(found_emojis)
        
        return text + ' ' + random.choice(emojis)


def load_config():
    """Load configuration and find active bot"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'philosophers.yaml')
    
    with open(config_path, 'r') as f:
        all_configs = yaml.safe_load(f)
    
    # Find first enabled bot
    for name, config in all_configs.items():
        if config.get('enabled', False):
            # Replace token from environment
            config['discord_token'] = os.getenv('DISCORD_TOKEN')
            if not config['discord_token']:
                raise ValueError("DISCORD_TOKEN not found in .env file")
            return config
    
    raise ValueError("No philosopher enabled in config! Set enabled: true for one in config/philosophers.yaml")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fast', action='store_true', help='Fast mode: minimal delays, always replies')
    args = parser.parse_args()

    print("=" * 60)
    print("Discord Philosophers - Synthetic Discourse Generator")
    print("=" * 60)
    print()

    # Load config
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure:")
        print("1. You have a .env file with DISCORD_TOKEN")
        print("2. You've enabled one philosopher in config/philosophers.yaml")
        return

    # Create and run bot
    bot = PhilosopherBot(config, fast_mode=args.fast)
    
    try:
        bot.run(config['discord_token'])
    except discord.LoginFailure:
        print("❌ Invalid Discord token. Check your .env file.")
    except Exception as e:
        print(f"❌ Error running bot: {e}")


if __name__ == '__main__':
    main()
