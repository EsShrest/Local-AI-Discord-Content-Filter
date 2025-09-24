# Discord Content Moderation Bot

AI-powered Discord bot using Ollama for intelligent content filtering with complete local processing.

## How It Works

### Information Flow
```
Discord Message → Pre-filtering → AI Analysis → Decision Logic → Action
```

1. **Message Reception**: Bot receives all Discord messages
2. **Smart Filtering**: Skips bot messages, admin users, and commands
3. **AI Analysis**: Sends message to local Ollama server for analysis
4. **Decision Making**: Uses confidence threshold (70%) to determine action
5. **Automated Response**: Deletes inappropriate content and warns user

### AI Analysis Process
- **Local Processing**: Uses Ollama (llama3:latest) running on localhost:11434
- **Context Awareness**: Understands intent, not just keywords
- **Multi-category Detection**: Profanity, hate speech, harassment, threats, spam
- **Confidence Scoring**: Only acts on high-confidence detections (>70%)

## Quick Setup

1. **Install Ollama** - Download from [ollama.ai](https://ollama.ai)
2. **Pull AI Model** - `ollama pull llama3:latest`
3. **Install Dependencies** - `pip install -r requirements.txt`
4. **Discord Bot Token** - Add your token to `Secret.txt`
5. **Run Bot** - `python app.py`

## Features

- **100% Local AI** - No external API calls, complete privacy
- **Real-time Moderation** - Processes messages in 2-3 seconds
- **Context Understanding** - AI comprehends meaning, not just keywords
- **Configurable Sensitivity** - Adjustable confidence thresholds
- **Admin Commands** - Testing and configuration tools
- **Detailed Logging** - Full transparency of all decisions

## Bot Permissions Required

- Read Messages
- Send Messages
- Manage Messages

## Commands (Admin Only)

- `!test_filter <message>` - Test content filter on specific text
- `!filter_stats` - Show Ollama connection and model status
- `!set_model <model>` - Switch between available AI models

## Example Flow

```
User: "This is fucking stupid!"
  ↓
Bot: Receives message → Not admin/command → Analyze
  ↓
AI: Analysis → 95% inappropriate (profanity)
  ↓
Bot: 95% > 70% threshold → DELETE + WARN
  ↓
Result: Message removed, user notified
```

## Privacy & Security

- **Local Processing**: All AI analysis happens on your machine
- **No Data Sharing**: Messages never leave your server
- **Token Protection**: Bot token excluded from repository
- **Open Source**: Full code transparency