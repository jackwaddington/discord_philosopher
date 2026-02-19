#!/usr/bin/env python3
"""
Quick test script to verify your setup before running the bot
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing imports...")
    try:
        import discord
        print("✅ discord.py installed")
    except ImportError:
        print("❌ discord.py not installed. Run: pip install discord.py")
        return False
    
    try:
        import yaml
        print("✅ PyYAML installed")
    except ImportError:
        print("❌ PyYAML not installed. Run: pip install PyYAML")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    try:
        import pytz
        print("✅ pytz installed")
    except ImportError:
        print("❌ pytz not installed. Run: pip install pytz")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists and has token"""
    print("\nTesting .env file...")
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env and add your Discord token")
        return False
    
    print("✅ .env file exists")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token or token == 'your_discord_bot_token_here':
        print("❌ DISCORD_TOKEN not set properly in .env")
        print("   Edit .env and replace 'your_discord_bot_token_here' with your actual token")
        return False
    
    print("✅ DISCORD_TOKEN is set")
    return True

def test_config():
    """Test if config file exists and has an enabled bot"""
    print("\nTesting configuration...")
    import yaml
    
    config_path = 'config/philosophers.yaml'
    if not os.path.exists(config_path):
        print(f"❌ Config file not found at {config_path}")
        return False
    
    print("✅ Config file exists")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    enabled_count = sum(1 for bot_config in config.values() if bot_config.get('enabled', False))
    
    if enabled_count == 0:
        print("❌ No philosopher is enabled in config")
        print("   Edit config/philosophers.yaml and set enabled: true for one philosopher")
        return False
    
    if enabled_count > 1:
        print(f"⚠️  Warning: {enabled_count} philosophers are enabled")
        print("   It's recommended to run only one philosopher per machine")
        print("   (though multiple will work)")
    
    for name, bot_config in config.items():
        if bot_config.get('enabled', False):
            print(f"✅ Enabled philosopher: {bot_config['profile']['name']}")
    
    return True

def test_ollama():
    """Test if Ollama is installed and has a model"""
    print("\nTesting Ollama...")
    import subprocess
    
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            
            # Check if any model is available
            if 'llama3' in result.stdout.lower():
                print("✅ llama3 model found")
                return True
            else:
                print("⚠️  No llama3 model found")
                print("   Run: ollama pull llama3:8b")
                print("   Or for Raspberry Pi: ollama pull llama3:3b")
                return False
        else:
            print("❌ Ollama command failed")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("   Install from: https://ollama.ai/")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Ollama command timed out")
        return False

def main():
    print("=" * 60)
    print("Discord Philosophers - Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    if not test_imports():
        all_good = False
        print("\n💡 Fix: pip install -r requirements.txt")
    
    if not test_env_file():
        all_good = False
    
    if not test_config():
        all_good = False
    
    if not test_ollama():
        all_good = False
    
    print()
    print("=" * 60)
    if all_good:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("You're ready to run the bot!")
        print("Run: python bot.py")
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        print()
        print("Please fix the issues above, then run this test again.")
        print("See SETUP.md for detailed instructions.")
    print()

if __name__ == '__main__':
    main()
