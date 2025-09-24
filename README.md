# Discord Content Moderation Bot

AI-powered Discord bot using Ollama for intelligent content filtering.

## Quick Setup

1. **Install Ollama** - Download from [ollama.ai](https://ollama.ai)
2. **Pull AI Model** - `ollama pull llama3:latest`
3. **Install Dependencies** - `pip install -r requirements.txt`
4. **Discord Bot Token** - Add your token to `Secret.txt`
5. **Run Bot** - `python app.py`

## Features

- Automatic content moderation using local AI
- Admin commands for testing and configuration
- Privacy-focused (runs entirely locally)
- Configurable filtering sensitivity

## Bot Permissions Required

- Read Messages
- Send Messages
- Manage Messages

## Commands

- `!test_filter <message>` - Test content filter
- `!filter_stats` - Show bot status
- `!set_model <model>` - Change AI model