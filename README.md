---
title: Voice Development Assistant
emoji: 🎤
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: "4.44.0"
app_file: app.py
pinned: true
license: mit
suggested_hardware: zero-a10g
suggested_storage: small
---

# 🎤 Voice Development Assistant

A personal voice interface for development workflows featuring Speech-to-Text, Text-to-Speech, and Claude AI integration.

## ✨ Features

- 🎤 **Speech-to-Text**: Real-time transcription using OpenAI Whisper (GPU accelerated with ZeroGPU)
- 🔊 **Text-to-Speech**: Natural voice synthesis using OpenAI TTS (6 voice options)
- 🤖 **Claude Integration**: Voice & text conversations with Claude AI
- 💬 **Multi-Modal**: Switch between voice and text interaction seamlessly
- 🚀 **ZeroGPU**: Optimized for Hugging Face's H200 GPU cluster
- 💻 **VS Code Extension**: Voice commands and dictation in your IDE
- ⚙️ **Configurable**: Swap between different TTS/STT providers

## 📁 Project Structure

```
Voice-Tool/
├── app.py                  # Main Gradio app (HF Spaces entry point)
├── core/                   # Core voice services
│   ├── stt_service.py     # Speech-to-text wrapper
│   ├── tts_service.py     # Text-to-speech wrapper
│   └── voice_manager.py   # Voice coordination
├── claude-bridge/          # Claude integration
│   ├── api_client.py      # Claude API client
│   └── bridge_server.py   # WebSocket/HTTP server
├── web-interface/          # Alternative web UI
│   └── app.py
├── vscode-extension/       # VS Code integration
│   ├── package.json
│   └── extension.js
├── config/                 # Configuration
│   └── settings.yaml
├── deployment/             # Deployment files
│   ├── requirements.txt
│   └── spaces_config.py
├── Dockerfile              # Container deployment
└── docker-compose.yml      # Local dev stack
```

## 🚀 Quick Start

### Option 1: Hugging Face Spaces (Recommended)

1. Fork this repository to your HuggingFace account
2. Create a new Space with Gradio SDK
3. Set secrets:
   - `OPENROUTER_API_KEY`: Your OpenRouter API key (for LLM)
4. Push and deploy!

### Option 2: Docker

```bash
# Clone the repo
git clone https://github.com/yourusername/Voice-Tool.git
cd Voice-Tool

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run with Docker Compose
docker-compose up -d

# Access at http://localhost:7860
```

### Option 3: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r deployment/requirements.txt

# Set environment variables
export OPENROUTER_API_KEY="your_key"

# Run the app
python app.py
```

## 🔧 Configuration

### Required API Keys

| Key | Required For | Get It From |
|-----|--------------|-------------|
| `OPENROUTER_API_KEY` | LLM (Claude, GPT-4, etc.) | [openrouter.ai](https://openrouter.ai/) |

### Free Components (No API Key Needed!)

| Component | Model |
|-----------|-------|
| **STT** | OpenAI Whisper (local) |
| **TTS** | HuggingFace SpeechT5 |

### Supported LLM Models via OpenRouter

- `anthropic/claude-sonnet-4-20250514` (Claude Sonnet 4)
- `anthropic/claude-3.5-sonnet` (Claude 3.5 Sonnet)
- `openai/gpt-4o` (GPT-4o)
- `openai/gpt-4o-mini` (GPT-4o Mini - cheaper)
- `google/gemini-pro-1.5` (Gemini Pro)
- `meta-llama/llama-3.1-70b-instruct` (Llama 3.1)
- And many more at [openrouter.ai/models](https://openrouter.ai/models)

### Optional Configuration

Edit `config/settings.yaml` to customize:
- STT provider (whisper, deepgram, browser)
- TTS provider (openai, elevenlabs, coqui)
- Claude model and parameters
- Server ports

## 📖 Usage

### Voice Chat
1. Click microphone to record
2. Speak your question
3. Claude responds with voice

### Transcription
- Upload audio or record via microphone
- GPU-accelerated Whisper transcription

### Text-to-Speech
- Enter text, choose voice
- Download generated audio

### Bridge Server (for integrations)
```bash
python claude-bridge/bridge_server.py
# HTTP API: http://localhost:8765
# WebSocket: ws://localhost:8766
```

## 🔒 Privacy & Security

- No persistent data storage
- Session-only conversation history
- All API calls encrypted
- Open source - verify the code

## 📄 License

MIT License - Free for personal use
