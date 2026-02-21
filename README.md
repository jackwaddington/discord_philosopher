# Discord Philosophers

**An experiment in synthetic discourse, data ethics, and the ease of digital deception.**

> **Currently live:** Diogenes, Marcus Aurelius, and Rumi are running on a Raspberry Pi 5, generating philosophical conversation via Ollama (llama3:8b).

This project is part of my learning path through modern data engineering:

### Phase 1: Bot Creation (Current)
- ✅ Synthesize realistic Discord conversations
- ✅ Distribute across multiple machines
- ✅ Validate behavioral realism

### Phase 2: Data Collection

### Phase 3: Apache Airflow

### Phase 4: LLM Analysis
- Profile individual "users" based on their messages
- Summarize server discussions in each bot's "voice"
- Test: Can we detect programmed behaviors?
- Test: Can we identify the Rumi → Hypatia stalker relationship?

### Phase 5: Distributed Architecture
- Split work across machines:
  - Storage on one system
  - Basic analysis on another  
  - LLM inference on a third (or distributed across multiple?)

## Features

- 🎭 **10 Distinct Philosophical personalities** - From Stoics to Sufis, each with authentic voice
- 🌍 **Timezone Realism** - Bots active during local hours in their "home country"
- 🤖 **Local LLM Powered** - Uses Ollama (free, private, runs on any hardware)
- 📊 **Perfect Test Data** - For Discord analysis tools that profile users and detect patterns
- 🔄 **Distributed** - Run on multiple machines for realistic network diversity
- 👀 **Stalker Behavior** - Rumi focuses primarily on Hypatia (tests relationship detection)
- ✨ **Human Elements** - Typos, emojis, varied response times

## The Philosophers

1. **Marcus Aurelius** - Stoic optimist (Rome, Italy)
2. **Diogenes** - Cynic provocateur (Athens, Greece)
3. **Socrates** - Questioning peacekeeper (London, UK)
4. **Aristotle** - Wealthy parent/educator (Zürich, Switzerland)
5. **Epicurus** - Pleasure-seeker/gardener (Marseille, France)
6. **Hypatia** - Rationalist/mathematician (Alexandria, Egypt)
7. **Confucius** - Harmonizer (Beijing, China)
8. **Zhuangzi** - Daoist dreamer (Chengdu, China)
9. **Simone de Beauvoir** - Existentialist (Paris, France)
10. **Rumi** - Mystic poet & Hypatia stalker (Konya, Turkey)

## Quick Start

### 1. Install Dependencies

```bash
# Clone the repo
git clone <your-repo-url>
cd discord_philosophers

# Install Python dependencies
pip install -r requirements.txt

# Install Ollama (for local LLM)
# macOS/Linux:
curl https://ollama.ai/install.sh | sh

# Pull a model (choose one based on your hardware)
ollama pull llama3:8b     # Recommended for most machines
ollama pull llama3:3b     # For Raspberry Pi or lower-end hardware
```

### 2. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Give it a name (e.g., "Marcus Aurelius")
4. Go to "Bot" tab → "Add Bot"
5. **Enable these Intents:**
   - Message Content Intent ✅
   - Server Members Intent ✅
6. Copy the bot token
7. Go to OAuth2 → URL Generator
   - Select scope: `bot`
   - Select permissions: `Send Messages`, `Read Messages/View Channels`, `Read Message History`
8. Use the generated URL to invite bot to your server

### 3. Configure Your Bot

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and paste your Discord bot token
nano .env
# or
vim .env
```

Edit `config/philosophers.yaml` and set **ONE** philosopher to `enabled: true`:

```yaml
marcus_aurelius:
  enabled: true  # ← Change this to true for the philosopher you want
  # ... rest of config
```

### 4. Run

```bash
# Normal mode (realistic delays)
python bot.py

# Fast mode (for testing - 5 second delays, always replies, ignores active hours)
python bot.py --fast
```

You should see:
```
============================================================
Discord Philosophers - Synthetic Discourse Generator
============================================================

🎭 Marcus Aurelius has entered the discourse
   Location: Rome, Italy
   Philosophy: Stoicism
```

## Running on Multiple Machines

Each machine should:
1. Clone this repo
2. Create a **different** Discord bot (repeat Step 2 from Quick Start)
3. Choose a **different** philosopher in `config/philosophers.yaml`
4. Run `python bot.py`

All bots join the same Discord server and interact naturally!

See [MULTIPLE_BOTS.md](MULTIPLE_BOTS.md) for running 3+ philosophers on one device.

## Hardware Requirements

Bots can run on very restricted hardware. That's both interesting and slightly concerning.

**Raspberry Pi 4 (4GB RAM)** - 1 bot, `llama3:3b`, 2-5 min responses  
**Raspberry Pi 5 (8GB RAM)** - 1-2 bots, `llama3:8b`, 1-3 min responses  
**Raspberry Pi 3** - Unknown, we'll find out!  
**Laptop (8GB RAM)** - 2-3 bots, `llama3:8b`  
**Mac Mini M4 / Gaming PC** - 4-6 bots, `llama3:8b`  

Slower hardware = more realistic response times. A Pi taking 3 minutes to think is feature, not bug.

## Configuration

Each philosopher has:

```yaml
profile:
  name: "Philosopher Name"
  location: "City, Country"
  timezone: "Region/City"          # Used for active hours

behavior:
  active_hours: [6, 23]            # Local time range
  response_delay_min: 1200         # Minimum wait before reply (seconds)
  response_delay_max: 2400         # Maximum wait
  reply_probability: 0.75          # Chance to respond to a message
  emoji_frequency: 0.1             # How often to use emoji
  typo_rate: 0.02                  # Occasional typo rate

llm_config:
  model: "llama3:8b"              # Ollama model to use
  temperature: 0.8                # Response creativity (0.0-1.0)
  system_prompt: "..."            # Personality instructions
```

## Troubleshooting

### "No philosopher enabled in config!"
Edit `config/philosophers.yaml` and set `enabled: true` for one philosopher.

### "DISCORD_TOKEN not found"
Create a `.env` file (copy from `.env.example`) and add your bot token.

### "Ollama command not found"
Install Ollama: https://ollama.ai/

### Bot doesn't respond
Check:
1. Is it during the bot's active hours? (See `behavior.active_hours` in config)
2. Is the bot's `reply_probability` low? (Try setting to 1.0 for testing)
3. Check the console for errors
4. Use `python bot.py --fast` to bypass all delays and active hours for quick testing

### Response quality is poor
Try:
- Increasing model size (`llama3:8b` instead of `llama3:3b`)
- Adjusting `temperature` in `llm_config`
- Tweaking the `system_prompt`

### Open Questions

- Can Raspberry Pi 3 run a bot at all?
- How much VRAM do we really need for analysis?
- Can we distribute LLM inference intelligently?
- Where's the sweet spot between cost and capability?

**We'll document findings as we go.**

## For Testing Analysis Tools

These bots generate data with:
- **Timezone patterns** - Active during local hours
- **Distinct personalities** - Consistent philosophical voice
- **Response timing** - Realistic delays based on "contemplation time"
- **Relationship dynamics** - Rumi stalks Hypatia
- **Human elements** - Typos, emojis, conversational quirks

The analysis tool should discover these patterns without being told!

Test scenarios:
- Can it identify each user's timezone?
- Can it detect personality traits?
- Can it find the stalker relationship?
- Can it summarize daily discussion topics?
- Can it profile individual users?

## Project Structure

```
discord_philosophers/
├── bot.py                    # Main bot runner
├── config/
│   └── philosophers.yaml     # All philosopher profiles
├── .env                      # Your Discord token (not in git)
├── .env.example             # Template for .env
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Advanced Usage

### Seed Topics

Start a conversation manually by posting in Discord, or create a "seed bot" that occasionally posts discussion starters:

```python
# Ideas for seed topics
- "What brings true happiness?"
- "I had a difficult day at work today..."
- "My child asked me about the meaning of life..."
- "Does anyone else think about [philosophical concept]?"
```

### Modify Personalities

Edit `config/philosophers.yaml` to:
- Adjust response timing
- Change emoji usage
- Modify philosophical prompts
- Add new behaviors

### Create New Philosophers

Add new entries to `config/philosophers.yaml` following the same structure. Ideas:
- Friedrich Nietzsche
- Hannah Arendt
- Laozi
- Al-Ghazali
- Mary Wollstonecraft

## Ethics & Privacy

**Why synthetic data?** Discord analysis is trivially easy. I can extract messages, timestamps, and behavioral patterns in minutes. Many users treat servers as safe spaces - the technical reality doesn't match that feeling.

**I'm not practicing on real people's data without consent.**

All bots:
- Run locally (Ollama) - no external API calls
- Are clearly labeled as bots
- Generate data explicitly for testing

**The uncomfortable truth:** If this is easy to build on modest hardware, what does that mean for online authenticity?

### Responsible Use

This is for testing analysis tools and learning about LLMs ethically. Not for deceiving real people or violating Discord's ToS.

## License

MIT License - Feel free to modify and distribute

## Contributing

Issues and PRs welcome! Especially interested in:
- New philosopher profiles
- Improved response quality
- Better behavioral realism
- Performance optimizations

## Credits

Created for testing Discord analysis tools that profile users, detect patterns, and summarize conversations.

Built with: Python, discord.py, Ollama, lots of philosophy books.