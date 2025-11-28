# Voice Development Wrapper

A personal voice interface wrapper for development workflows, featuring TTS/STT capabilities, VS Code integration, and Claude Desktop connectivity.

## Features

- 🎤 **Speech-to-Text**: Real-time voice input using OpenAI Whisper or browser APIs
- 🔊 **Text-to-Speech**: Natural voice output using modern TTS engines
- 💻 **VS Code Extension**: Voice commands and dictation in your IDE
- 🤖 **Claude Integration**: Direct voice interaction with Claude Desktop/API
- 🚀 **Hugging Face Spaces**: Easy deployment for remote access
- ⚙️ **Configurable**: Swap between different TTS/STT providers

## Project Structure

```
voice-dev-wrapper/
├── core/                   # Core voice service
│   ├── tts_service.py     # Text-to-speech wrapper
│   ├── stt_service.py     # Speech-to-text wrapper
│   └── voice_manager.py   # Main voice coordination
├── vscode-extension/      # VS Code integration
│   ├── src/
│   ├── package.json
│   └── extension.js
├── claude-bridge/         # Claude Desktop integration
│   ├── api_client.py
│   └── bridge_server.py
├── web-interface/         # Hugging Face Spaces UI
│   ├── app.py
│   ├── static/
│   └── templates/
├── config/               # Configuration files
│   └── settings.yaml
└── deployment/          # Deployment scripts
    ├── requirements.txt
    └── spaces_config.py
```

## Quick Start

1. Clone and install dependencies
2. Configure your API keys in `config/settings.yaml`
3. Run the core service: `python core/voice_manager.py`
4. Install VS Code extension from `vscode-extension/`
5. Deploy to Hugging Face Spaces using `deployment/`

## Personal Development Tool

This is designed as a personal productivity tool to speed up development workflows through voice interaction. Easily extendable and customizable for your specific needs.
