import discord
from discord.ext import commands
import requests
import json
import asyncio
import logging
import os
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Ollama configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3:latest"  # You can change this to any model you have installed

class ContentFilter:
    def __init__(self, ollama_url: str, model: str):
        self.ollama_url = ollama_url
        self.model = model
        
    async def check_content(self, message: str) -> dict:
        """
        Check if content contains inappropriate language using Ollama
        Returns: dict with 'is_inappropriate', 'confidence', 'reason'
        """
        prompt = f"""
Analyze the following message for inappropriate content including:
- Profanity and vulgar language
- Hate speech
- Harassment or bullying
- Sexual content
- Violence or threats
- Spam or excessive repetition

Message: "{message}"

Respond with only a JSON object in this exact format:
{{"is_inappropriate": true/false, "confidence": 0.0-1.0, "reason": "brief explanation"}}
"""
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.1
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                try:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx != 0:
                        json_str = response_text[start_idx:end_idx]
                        parsed_result = json.loads(json_str)
                        return parsed_result
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse Ollama response: {response_text[:100]}...")
                    
            return {"is_inappropriate": False, "confidence": 0.0, "reason": "Analysis failed"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return {"is_inappropriate": False, "confidence": 0.0, "reason": "Service unavailable"}
        except Exception as e:
            logger.error(f"Content filtering error: {e}")
            return {"is_inappropriate": False, "confidence": 0.0, "reason": "Unknown error"}

# Initialize content filter
content_filter = ContentFilter(OLLAMA_URL, OLLAMA_MODEL)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    
    # Test Ollama connection
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            logger.info(f"Ollama connected. Available models: {model_names}")
            
            if OLLAMA_MODEL not in model_names:
                logger.warning(f"Model '{OLLAMA_MODEL}' not found. Available: {model_names}")
            else:
                logger.info(f"Using model: {OLLAMA_MODEL}")
        else:
            logger.error("Failed to connect to Ollama")
    except Exception as e:
        logger.error(f"Ollama connection test failed: {e}")

@bot.event
async def on_message(message):
    # Don't process messages from the bot itself
    if message.author == bot.user:
        return
    
    # Skip bot messages, admin messages, and commands
    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return
    
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    # Filter message content
    if message.content.strip():
        result = await content_filter.check_content(message.content)
        
        if result.get('is_inappropriate', False) and result.get('confidence', 0) > 0.7:
            try:
                await message.delete()
                
                warning_msg = await message.channel.send(
                    f"{message.author.mention}, your message was removed due to policy violation.",
                    delete_after=10
                )
                
                logger.info(f"Content filtered - User: {message.author}, Reason: {result.get('reason')}")
                
            except discord.errors.NotFound:
                pass
            except discord.errors.Forbidden:
                logger.error("Insufficient permissions to delete messages")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    await bot.process_commands(message)

@bot.command(name='test_filter')
@commands.has_permissions(manage_messages=True)
async def test_filter(ctx, *, test_message: str):
    """Test the content filter with a message (Admin only)"""
    result = await content_filter.check_content(test_message)
    
    embed = discord.Embed(
        title="Content Filter Test",
        color=discord.Color.red() if result.get('is_inappropriate') else discord.Color.green()
    )
    embed.add_field(name="Message", value=f"```{test_message[:500]}```", inline=False)
    embed.add_field(name="Inappropriate", value=result.get('is_inappropriate', False), inline=True)
    embed.add_field(name="Confidence", value=f"{result.get('confidence', 0):.2%}", inline=True)
    embed.add_field(name="Reason", value=result.get('reason', 'N/A'), inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='filter_stats')
@commands.has_permissions(manage_messages=True)
async def filter_stats(ctx):
    """Show filter statistics (Admin only)"""
    embed = discord.Embed(
        title="Content Filter Status",
        color=discord.Color.blue()
    )
    
    # Test Ollama connection
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            embed.add_field(name="Ollama Status", value="Connected", inline=True)
            embed.add_field(name="Current Model", value=OLLAMA_MODEL, inline=True)
            embed.add_field(name="Available Models", value=f"{len(models)} models", inline=True)
        else:
            embed.add_field(name="Ollama Status", value="Connection Error", inline=True)
    except Exception as e:
        embed.add_field(name="Ollama Status", value=f"Error: {str(e)[:50]}", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='set_model')
@commands.has_permissions(administrator=True)
async def set_model(ctx, model_name: str):
    """Change the Ollama model used for filtering (Admin only)"""
    global OLLAMA_MODEL
    
    try:
        # Check if model exists
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model['name'].split(':')[0] for model in models]
            
            if model_name in model_names:
                OLLAMA_MODEL = model_name
                content_filter.model = model_name
                await ctx.send(f"Model changed to: {model_name}")
            else:
                await ctx.send(f"Model '{model_name}' not found. Available: {', '.join(model_names)}")
        else:
            await ctx.send("Failed to connect to Ollama")
    except Exception as e:
        await ctx.send(f"Error: {e}")

def load_token():
    """Load Discord bot token from Secret.txt"""
    try:
        with open('Secret.txt', 'r') as f:
            token = f.read().strip()
            if token:
                return token
            else:
                raise ValueError("Token file is empty")
    except FileNotFoundError:
        logger.error("Secret.txt file not found")
        return None
    except Exception as e:
        logger.error(f"Error reading token: {e}")
        return None

if __name__ == "__main__":
    # Load the bot token
    token = load_token()
    
    if not token:
        logger.error("No Discord bot token found. Please add your token to Secret.txt")
        exit(1)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token")
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
