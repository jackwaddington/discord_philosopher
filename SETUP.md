# Detailed Setup Guide

## Step-by-Step Setup for Each Machine

### Prerequisites Check

Before starting, verify you have:
- [ ] Python 3.8 or higher (`python3 --version`)
- [ ] pip installed (`pip3 --version`)
- [ ] Git installed (optional, for cloning)

### 1. Get the Code

**Option A: Clone from GitHub**
```bash
git clone git@github.com:jackwaddington/discord_philosopher.git
cd discord_philosophers
```

**Option B: Download ZIP**
1. Download the repository as ZIP
2. Extract it
3. Open terminal/command prompt in that folder

### 2. Install Python Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# Or if using pip3:
pip3 install -r requirements.txt
```

Expected output:
```
Successfully installed discord.py-2.3.0 PyYAML-6.0 python-dotenv-1.0.0 pytz-2023.3
```

### 3. Install Ollama

**macOS:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

**Raspberry Pi:**
```bash
curl https://ollama.ai/install.sh | sh
```

### 4. Download LLM Model

**For most machines (8GB+ RAM):**
```bash
ollama pull llama3:8b
```

**For Raspberry Pi or low-RAM machines:**
```bash
ollama pull llama3:3b
```

**To verify it's working:**
```bash
ollama list
```

You should see your downloaded model listed.

### 5. Create Discord Bot

#### Step-by-step with screenshots descriptions:

1. **Go to Discord Developer Portal**
   - Navigate to: https://discord.com/developers/applications
   - Log in with your Discord account

2. **Create New Application**
   - Click blue "New Application" button (top right)
   - Name it after your philosopher (e.g., "Marcus Aurelius")
   - Click "Create"

3. **Navigate to Bot Section**
   - In left sidebar, click "Bot"
   - Click "Add Bot" button
   - Confirm "Yes, do it!"

4. **Enable Required Intents**
   - Scroll down to "Privileged Gateway Intents"
   - Enable these THREE checkboxes:
     - ✅ Presence Intent
     - ✅ Server Members Intent
     - ✅ Message Content Intent
   - Click "Save Changes"

5. **Copy Bot Token**
   - Scroll back up to "Token" section
   - Click "Reset Token" (first time) or "Copy" (if already created)
   - **IMPORTANT:** Save this token somewhere safe!
   - You'll paste it in `.env` file in next step

6. **Generate Invite URL**
   - In left sidebar, click "OAuth2" → "URL Generator"
   - Under "Scopes", check:
     - ✅ bot
   - Under "Bot Permissions", check:
     - ✅ Read Messages/View Channels
     - ✅ Send Messages
     - ✅ Read Message History
   - Copy the generated URL at the bottom

7. **Invite Bot to Server**
   - Paste the URL in your browser
   - Select your test Discord server
   - Click "Authorize"
   - Complete the captcha

### 6. Configure the Bot

1. **Create .env file:**
```bash
cp .env.example .env
```

2. **Edit .env file:**

**macOS/Linux:**
```bash
nano .env
```

**Windows:**
```bash
notepad .env
```

3. **Paste your Discord token:**
```
DISCORD_TOKEN=abcd123abcd
```
(Replace with your actual token from step 5)

4. **Save and close**
   - nano: Press `Ctrl+X`, then `Y`, then `Enter`
   - notepad: File → Save

### 7. Choose Your Philosopher

Edit `config/philosophers.yaml`:

```bash
nano config/philosophers.yaml
```

Find the philosopher you want and change `enabled: false` to `enabled: true`:

```yaml
marcus_aurelius:
  enabled: true  # ← Change this line!
  discord_token: "${DISCORD_TOKEN}"
  # ... rest of config
```

**IMPORTANT:** Only enable ONE philosopher per machine!

### 8. Test Run

```bash
python bot.py
```

**Expected output:**
```
============================================================
Discord Philosophers - Synthetic Discourse Generator
============================================================

🎭 Marcus Aurelius has entered the discourse
   Location: Rome, Italy
   Philosophy: Stoicism
```

If you see this, SUCCESS! 🎉

### 9. Verify in Discord

1. Go to your Discord server
2. You should see your bot in the member list (appears offline until active)
3. Say something in a channel the bot can see
4. Wait for the bot's response delay (could be 20-40 minutes depending on philosopher)

## Common Issues & Solutions

### Issue: "Module not found: discord"
**Solution:**
```bash
pip install discord.py
```

### Issue: "Ollama command not found"
**Solution:** 
- Install Ollama (see step 3)
- Add to PATH if needed
- Restart terminal

### Issue: "No philosopher enabled in config"
**Solution:**
- Edit `config/philosophers.yaml`
- Find your philosopher
- Change `enabled: false` to `enabled: true`
- Save file

### Issue: "DISCORD_TOKEN not found in .env file"
**Solution:**
- Make sure `.env` file exists (not `.env.example`)
- Check that your token is on the line `DISCORD_TOKEN=...`
- No spaces around the `=`
- No quotes around the token

### Issue: Bot connects but doesn't respond
**Possible causes:**
1. **Not in active hours** - Check `active_hours` in config
2. **Low reply probability** - Set `reply_probability: 1.0` for testing
3. **Wrong channel permissions** - Make sure bot can read/send in that channel

### Issue: "Invalid Discord token"
**Solution:**
- Go back to Discord Developer Portal
- Bot section → Reset Token
- Copy the NEW token
- Paste in `.env` file

### Issue: Ollama model generates errors
**Solution:**
- Verify model is downloaded: `ollama list`
- Try a smaller model: `ollama pull llama3:3b`
- Update model name in config: `model: "llama3:3b"`

## Running on Specific Platforms

### Raspberry Pi Specific

```bash
# Use smaller model
ollama pull llama3:3b

# Edit philosopher config
nano config/philosophers.yaml

# Change model line to:
model: "llama3:3b"  # Under llm_config section
```

### macOS Specific

If you get SSL certificate errors:
```bash
pip install --upgrade certifi
```

### Windows Specific

Use PowerShell or Command Prompt, not Git Bash.

If Python isn't recognized:
```bash
py -m pip install -r requirements.txt
py bot.py
```

## Running Multiple Bots on One Machine

You CAN run multiple bots on one machine:

1. Create separate folders:
```bash
cp -r discord_philosophers discord_philosophers_marcus
cp -r discord_philosophers discord_philosophers_socrates
```

2. Each folder gets:
   - Its own `.env` with different bot token
   - Different philosopher enabled in config

3. Run each in separate terminal:
```bash
# Terminal 1
cd discord_philosophers_marcus
python bot.py

# Terminal 2
cd discord_philosophers_socrates
python bot.py
```

## Keeping Bots Running 24/7

### Using screen (Linux/Mac)

```bash
# Start a screen session
screen -S marcus

# Run bot
python bot.py

# Detach: Press Ctrl+A, then D

# Reattach later
screen -r marcus
```

### Using systemd (Linux)

Create `/etc/systemd/system/philosopher-bot.service`:

```ini
[Unit]
Description=Marcus Aurelius Discord Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/discord_philosophers
ExecStart=/usr/bin/python3 /path/to/discord_philosophers/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable philosopher-bot
sudo systemctl start philosopher-bot
```

## Next Steps

Once your bot is running:
1. Invite your friends to run other philosophers
2. Let them chat for a few days
3. Use your Discord analysis tool to study the data
4. Observe if it detects:
   - Timezone patterns
   - Personality traits
   - The Rumi → Hypatia stalker relationship
   - Topic trends over time

## Getting Help

If you're stuck:
1. Check this guide again
2. Review the main README.md
3. Check Discord Developer Portal for bot status
4. Verify Ollama is running: `ollama list`
5. Check bot logs in terminal for error messages

## Testing Checklist

Before considering your bot "production ready":

- [ ] Bot appears in Discord server member list
- [ ] Bot responds to at least one message
- [ ] Responses are in-character for the philosopher
- [ ] Timing delays feel realistic
- [ ] Emojis appear occasionally
- [ ] No error messages in console
- [ ] Bot respects active hours (test by changing timezone)

Good luck! 🎭📚
