# Running Multiple Philosophers on One Device

This guide covers how to run 3+ philosopher bots on a single machine.

## Why Run Multiple on One Machine?

- **Mac Mini M4 / Gaming PC** - Plenty of resources for 2-4 bots
- **Faster testing** - Don't need to coordinate with multiple friends
- **Cost effective** - One machine, multiple philosophers

## Method 1: Separate Folders (Recommended)

This is the simplest approach - each bot gets its own folder.

### Setup

```bash
# Clone the repo once
git clone https://github.com/yourusername/discord_philosophers.git

# Create copies for each philosopher
cp -r discord_philosophers discord_philosophers_marcus
cp -r discord_philosophers discord_philosophers_socrates
cp -r discord_philosophers discord_philosophers_diogenes

# You now have:
# discord_philosophers_marcus/
# discord_philosophers_socrates/
# discord_philosophers_diogenes/
```

### Configure Each Bot

**For Marcus Aurelius:**
```bash
cd discord_philosophers_marcus
cp .env.example .env
nano .env  # Paste Discord bot token #1

# Edit config to enable Marcus
nano config/philosophers.yaml
# Set marcus_aurelius: enabled: true
# Make sure all others are enabled: false
```

**For Socrates:**
```bash
cd ../discord_philosophers_socrates
cp .env.example .env
nano .env  # Paste Discord bot token #2

# Edit config to enable Socrates
nano config/philosophers.yaml
# Set socrates: enabled: true
```

**For Diogenes:**
```bash
cd ../discord_philosophers_diogenes
cp .env.example .env
nano .env  # Paste Discord bot token #3

# Edit config to enable Diogenes
nano config/philosophers.yaml
# Set diogenes: enabled: true
```

### Run All Three

You need **3 separate terminal windows/tabs**:

**Terminal 1:**
```bash
cd discord_philosophers_marcus
python bot.py
```

**Terminal 2:**
```bash
cd discord_philosophers_socrates
python bot.py
```

**Terminal 3:**
```bash
cd discord_philosophers_diogenes
python bot.py
```

## Keeping Them Running 24/7

When you close the terminal, the bots stop. Use `screen` or `tmux` to keep them running.

### Using screen (Easiest)

**Start each bot in its own screen session:**

```bash
# Start Marcus
screen -S marcus
cd discord_philosophers_marcus
python bot.py
# Press: Ctrl+A, then D (to detach)

# Start Socrates
screen -S socrates
cd discord_philosophers_socrates
python bot.py
# Press: Ctrl+A, then D

# Start Diogenes
screen -S diogenes
cd discord_philosophers_diogenes
python bot.py
# Press: Ctrl+A, then D
```

**Check running sessions:**
```bash
screen -ls
```

Output:
```
There are screens on:
    12345.marcus    (Detached)
    12346.socrates  (Detached)
    12347.diogenes  (Detached)
```

**Reattach to any bot:**
```bash
screen -r marcus    # View Marcus's console
screen -r socrates  # View Socrates's console
screen -r diogenes  # View Diogenes's console
```

**Kill a session:**
```bash
screen -X -S marcus quit
```

### Using tmux (Alternative)

**Start each bot:**
```bash
# Marcus
tmux new -s marcus
cd discord_philosophers_marcus && python bot.py
# Press: Ctrl+B, then D

# Socrates
tmux new -s socrates
cd discord_philosophers_socrates && python bot.py
# Press: Ctrl+B, then D

# Diogenes
tmux new -s diogenes
cd discord_philosophers_diogenes && python bot.py
# Press: Ctrl+B, then D
```

**List sessions:**
```bash
tmux ls
```

**Reattach:**
```bash
tmux attach -t marcus
```

## Quick Start/Stop Scripts

Create helper scripts to manage all bots at once.

**start_all.sh:**
```bash
#!/bin/bash

echo "Starting all philosophers..."

screen -dmS marcus bash -c "cd discord_philosophers_marcus && python bot.py"
screen -dmS socrates bash -c "cd discord_philosophers_socrates && python bot.py"
screen -dmS diogenes bash -c "cd discord_philosophers_diogenes && python bot.py"

echo "All bots started!"
echo "View them with: screen -ls"
echo "Attach to one: screen -r marcus"
```

**stop_all.sh:**
```bash
#!/bin/bash

echo "Stopping all philosophers..."

screen -X -S marcus quit
screen -X -S socrates quit
screen -X -S diogenes quit

echo "All bots stopped!"
```

**Make them executable:**
```bash
chmod +x start_all.sh stop_all.sh
```

**Usage:**
```bash
./start_all.sh   # Start all bots
./stop_all.sh    # Stop all bots
screen -ls       # Check status
```

## Resource Considerations

### RAM Usage (approximate)
- Each bot: ~500MB-1GB (depending on LLM model)
- 3 bots with llama3:8b: ~3-4GB RAM total
- 3 bots with llama3:3b: ~1.5-2GB RAM total

### CPU Usage
- Mostly idle (waiting for messages)
- Spikes when generating responses
- LLM generation can use 100% of one core for 10-60 seconds

### Recommendations by Hardware

**Mac Mini M4 (24GB RAM):**
- Run 4-6 bots comfortably
- Use llama3:8b model
- Plenty of headroom

**Gaming PC (16GB RAM, RTX 5060 Ti):**
- Run 3-4 bots easily
- Use llama3:8b model
- GPU barely used (Ollama uses CPU by default)

**Older Laptop (8GB RAM):**
- Run 2-3 bots max
- Use llama3:3b model
- Close other applications

**Raspberry Pi 4 (4GB/8GB):**
- Run 1-2 bots max
- Use llama3:3b model
- Responses will be slower (feature, not bug!)

## Troubleshooting

### "Bot won't start - port already in use"
Discord bots don't use ports. You have a different issue - check the error message.

### "All bots have same personality"
Check that each folder has different philosopher enabled in `config/philosophers.yaml`.

### "Bot #2 and #3 won't connect"
Make sure you created **separate Discord bot applications** with **different tokens**.

### "System running slow"
- Reduce number of bots
- Use smaller LLM model (llama3:3b)
- Check `top` or Activity Monitor for resource hogs

### "Can't remember which screen is which"
```bash
screen -ls           # List all
screen -r marcus     # Try each by name
```

## Auto-Start on Boot (Advanced)

### Using cron (Mac/Linux)

```bash
crontab -e
```

Add:
```
@reboot /path/to/discord_philosophers/start_all.sh
```

### Using systemd (Linux)

Create `/etc/systemd/system/philosophers.service`:

```ini
[Unit]
Description=Discord Philosophers
After=network.target

[Service]
Type=forking
User=youruser
WorkingDirectory=/home/youruser
ExecStart=/home/youruser/start_all.sh
ExecStop=/home/youruser/stop_all.sh

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable philosophers
sudo systemctl start philosophers
```

## Monitoring All Bots

**Quick health check script (check_bots.sh):**
```bash
#!/bin/bash

echo "=== Philosopher Bot Status ==="
echo

for bot in marcus socrates diogenes; do
    if screen -list | grep -q "$bot"; then
        echo "✅ $bot is running"
    else
        echo "❌ $bot is NOT running"
    fi
done

echo
echo "Detailed list:"
screen -ls
```

Make executable:
```bash
chmod +x check_bots.sh
./check_bots.sh
```

## Disk Space

Each folder is ~50KB (just Python code). Very minimal disk usage.

## Network Usage

Negligible - just Discord API calls (a few KB per message).

## Best Practices

1. **Stagger start times** - Don't start all 3 at exact same time
   ```bash
   screen -dmS marcus bash -c "cd discord_philosophers_marcus && python bot.py"
   sleep 30
   screen -dmS socrates bash -c "cd discord_philosophers_socrates && python bot.py"
   sleep 30
   screen -dmS diogenes bash -c "cd discord_philosophers_diogenes && python bot.py"
   ```

2. **Different timezones** - Choose philosophers from different timezones for more realistic patterns

3. **Monitor logs** - Occasionally check each screen session to see if there are errors

4. **Restart weekly** - Kill and restart bots once a week to clear any memory leaks

## Summary

Running multiple bots on one machine:
- ✅ Easy with separate folders
- ✅ Use `screen` to keep them running
- ✅ Create start/stop scripts for convenience
- ✅ Monitor with `screen -ls`
- ✅ Mac Mini M4 can handle 4-6 bots easily

Happy philosophizing! 🎭
