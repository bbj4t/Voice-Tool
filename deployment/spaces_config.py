"""
Hugging Face Spaces Configuration
Setup and deployment helpers for HF Spaces
"""

import os
import yaml
from pathlib import Path

# Hugging Face Spaces README template
README_TEMPLATE = """---
title: Voice Development Assistant
emoji: 🎤
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.19.0
app_file: web-interface/app.py
pinned: false
license: mit
---

# Voice Development Assistant

A personal development tool featuring voice-enabled Claude integration with TTS/STT capabilities.

## Features

- 🎤 **Speech-to-Text**: Real-time voice transcription using OpenAI Whisper
- 🔊 **Text-to-Speech**: Natural voice synthesis using OpenAI TTS
- 🤖 **Claude Integration**: Voice conversations with Claude AI
- 💬 **Multi-Modal**: Both voice and text interaction modes
- ⚙️ **Configurable**: Easy switching between TTS/STT providers

## Setup

1. Set your API keys as Hugging Face Spaces secrets:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `OPENAI_API_KEY`: Your OpenAI API key

2. The app will automatically connect to these services

## Usage

### Voice Chat
Speak directly to Claude and receive voice responses in real-time.

### Transcription
Upload audio files or use your microphone for accurate speech-to-text conversion.

### Text-to-Speech
Convert any text to natural-sounding speech with multiple voice options.

### Text Chat
Traditional text-based conversation interface with Claude.

## Technical Details

- **STT**: OpenAI Whisper (base model)
- **TTS**: OpenAI TTS (multiple voices available)
- **AI**: Claude Sonnet 4
- **Framework**: Gradio

## Privacy

This is a personal development tool. Conversations are processed through OpenAI and Anthropic APIs.
No data is stored persistently by this application.

## License

MIT License - Personal use
"""


def create_spaces_readme(output_path: str = None):
    """Create README.md for Hugging Face Spaces"""
    output_path = output_path or Path(__file__).parent.parent / "README_SPACES.md"
    
    with open(output_path, 'w') as f:
        f.write(README_TEMPLATE)
    
    print(f"Spaces README created at: {output_path}")
    return output_path


def create_env_template():
    """Create .env template file"""
    env_template = """# Voice Development Assistant - Environment Variables
# Copy this file to .env and fill in your API keys

# Required: Anthropic API Key for Claude
ANTHROPIC_API_KEY=your_anthropic_key_here

# Required: OpenAI API Key for Whisper STT and TTS
OPENAI_API_KEY=your_openai_key_here

# Optional: Hugging Face token for model access
HUGGINGFACE_TOKEN=your_hf_token_here

# Optional: Deepgram API Key (if using Deepgram STT)
# DEEPGRAM_API_KEY=your_deepgram_key_here

# Optional: ElevenLabs API Key (if using ElevenLabs TTS)
# ELEVENLABS_API_KEY=your_elevenlabs_key_here
"""
    
    env_path = Path(__file__).parent.parent / ".env.template"
    with open(env_path, 'w') as f:
        f.write(env_template)
    
    print(f"Environment template created at: {env_path}")
    return env_path


def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Environment variables
.env
*.env

# API Keys and secrets
config/secrets.yaml
*.key
*.pem

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Audio files (for testing)
*.wav
*.mp3
*.ogg
*.flac

# Temporary files
tmp/
temp/
*.tmp

# Model files (if downloaded locally)
models/
*.pt
*.pth
*.ckpt

# VS Code extension
vscode-extension/node_modules/
vscode-extension/out/
vscode-extension/*.vsix
"""
    
    gitignore_path = Path(__file__).parent.parent / ".gitignore"
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content)
    
    print(f"Gitignore created at: {gitignore_path}")
    return gitignore_path


def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    dockerfile_content = """FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    ffmpeg \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY deployment/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY core/ ./core/
COPY claude-bridge/ ./claude-bridge/
COPY web-interface/ ./web-interface/
COPY config/ ./config/

# Expose ports
EXPOSE 7860 8765 8766

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run the application
CMD ["python", "web-interface/app.py"]
"""
    
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    with open(dockerfile_path, 'w') as f:
        f.write(dockerfile_content)
    
    print(f"Dockerfile created at: {dockerfile_path}")
    return dockerfile_path


def setup_spaces_deployment():
    """Complete setup for Hugging Face Spaces deployment"""
    print("Setting up Hugging Face Spaces deployment...")
    
    create_spaces_readme()
    create_env_template()
    create_gitignore()
    create_dockerfile()
    
    print("\n✅ Deployment setup complete!")
    print("\nNext steps:")
    print("1. Create a new Space on Hugging Face")
    print("2. Set your API keys as Space secrets:")
    print("   - ANTHROPIC_API_KEY")
    print("   - OPENAI_API_KEY")
    print("3. Push this repository to your Space")
    print("4. The app will automatically deploy!")
    print("\nFor local testing:")
    print("1. Copy .env.template to .env")
    print("2. Fill in your API keys")
    print("3. Run: python web-interface/app.py")


if __name__ == "__main__":
    setup_spaces_deployment()
