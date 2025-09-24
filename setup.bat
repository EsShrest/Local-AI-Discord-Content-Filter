
@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Pulling AI model...
ollama pull llama3:latest

echo Setup complete! Add your Discord bot token to Secret.txt
pause