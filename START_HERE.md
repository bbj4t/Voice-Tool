# 🎤 Voice Development Wrapper

> **Personal voice interface for development workflows with TTS, STT, and Claude AI integration**

---

## 📋 Table of Contents

- [Quick Links](#quick-links)
- [What is This?](#what-is-this)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Use Cases](#use-cases)
- [Requirements](#requirements)

---

## 🔗 Quick Links

### Get Started
- **[QUICK_START.py](quick_start.py)** - Run this first! Validates setup and shows next steps
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive usage documentation

### Setup & Configuration
- **[deployment/setup.py](deployment/setup.py)** - Automated installation script
- **[test_installation.py](test_installation.py)** - Verify your installation
- **[config/settings.yaml](config/settings.yaml)** - Configuration file

### Code & Examples
- **[examples/example_usage.py](examples/example_usage.py)** - 10+ working examples
- **[web-interface/app.py](web-interface/app.py)** - Launch web UI
- **[claude-bridge/bridge_server.py](claude-bridge/bridge_server.py)** - Start voice server

---

## 🎯 What is This?

A comprehensive, production-ready voice development tool that enables:

✅ **Voice-to-Code** - Dictate code in VS Code  
✅ **Claude Conversations** - Talk to Claude AI naturally  
✅ **Speech-to-Text** - Transcribe audio with Whisper  
✅ **Text-to-Speech** - Natural voice synthesis  
✅ **Web Interface** - Beautiful Gradio UI  
✅ **API Access** - WebSocket & HTTP APIs  
✅ **VS Code Extension** - Voice controls in your IDE  
✅ **Cloud Ready** - Deploy to Hugging Face Spaces  

**Built for:** Personal productivity and development workflows  
**Tech Stack:** Python, Whisper, OpenAI TTS, Claude API, Gradio, WebSocket

---

## ✨ Features

### 🎤 Speech-to-Text (STT)
- **Whisper** (offline, high accuracy)
- **Deepgram** (cloud, real-time)
- **Browser API** (web-based)
- Multiple model sizes (tiny → large)
- Support for 90+ languages

### 🔊 Text-to-Speech (TTS)
- **OpenAI TTS** (6 natural voices)
- **ElevenLabs** (premium quality)
- **Coqui** (open-source)
- Speed control
- Voice customization

### 🤖 Claude Integration
- Voice conversations
- Text chat
- Streaming responses
- Conversation history
- Export/import sessions

### 💻 VS Code Extension
- Voice-activated coding
- Code dictation mode
- Ask Claude about code
- Keyboard shortcuts
- Status bar integration

### 🌐 Web Interface
- Voice chat tab
- Transcription tool
- Speech synthesis
- Text chat
- Mobile-friendly

### 🔌 APIs
- WebSocket for real-time
- HTTP REST endpoints
- Python client library
- JavaScript examples

---

## 🚀 Quick Start

### 1️⃣ First Time Setup (2 minutes)

```bash
# Option A: Automated setup
python deployment/setup.py

# Option B: Manual setup
pip install -r deployment/requirements.txt
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

### 2️⃣ Verify Installation

```bash
python test_installation.py
```

### 3️⃣ Launch!

**Web Interface** (Recommended for first-time users)
```bash
python web-interface/app.py
# Opens at http://localhost:7860
```

**Voice Server** (For API/VS Code usage)
```bash
python claude-bridge/bridge_server.py
# HTTP: http://localhost:8765
# WebSocket: ws://localhost:8766
```

**Quick Help**
```bash
python quick_start.py
```

### 4️⃣ Try Examples

```bash
python examples/example_usage.py
```

---

## 📁 Project Structure

```
voice-dev-wrapper/
│
├── 📄 README.md                    ← You are here!
├── 📄 PROJECT_SUMMARY.md           ← Complete project overview
├── 📄 USAGE_GUIDE.md               ← Detailed usage guide
├── 🚀 quick_start.py               ← First run this
├── ✅ test_installation.py         ← Verify setup
│
├── 🎤 core/                        ← Voice services
│   ├── stt_service.py              │  Speech-to-text
│   ├── tts_service.py              │  Text-to-speech
│   └── voice_manager.py            │  Coordination
│
├── 🤖 claude-bridge/               ← Claude integration
│   ├── api_client.py               │  Claude API client
│   └── bridge_server.py            │  WebSocket/HTTP server
│
├── 💻 vscode-extension/            ← VS Code extension
│   ├── package.json                │  Extension manifest
│   └── src/extension.js            │  Extension code
│
├── 🌐 web-interface/               ← Gradio web UI
│   └── app.py                      │  Web application
│
├── ⚙️ config/                      ← Configuration
│   └── settings.yaml               │  Central config
│
├── 🚢 deployment/                  ← Deployment tools
│   ├── setup.py                    │  Automated setup
│   ├── spaces_config.py            │  HuggingFace config
│   └── requirements.txt            │  Dependencies
│
└── 📚 examples/                    ← Code examples
    └── example_usage.py            │  10+ examples
```

---

## 📚 Documentation

### Core Documentation
1. **[README.md](README.md)** (this file) - Start here
2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete overview
3. **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed instructions

### Getting Started
- **Installation:** Run `deployment/setup.py`
- **Configuration:** Edit `config/settings.yaml`
- **Testing:** Run `test_installation.py`
- **Examples:** Check `examples/example_usage.py`

### API Documentation
- **Python API:** See USAGE_GUIDE.md § API Reference
- **WebSocket API:** See USAGE_GUIDE.md § WebSocket API
- **HTTP API:** See USAGE_GUIDE.md § HTTP API Endpoints

### Deployment Guides
- **Local:** USAGE_GUIDE.md § Local Server
- **Docker:** USAGE_GUIDE.md § Docker
- **HuggingFace:** USAGE_GUIDE.md § Hugging Face Spaces

---

## 💡 Use Cases

### 1. Voice Coding in VS Code
```
1. Press Ctrl+Shift+V
2. Say: "Create a function that sorts a list"
3. Code appears automatically
```

### 2. Audio Transcription
```
1. Open web interface
2. Upload audio file
3. Get accurate transcription
```

### 3. Claude Conversations
```
1. Record voice message
2. Claude responds in text and voice
3. Natural back-and-forth
```

### 4. Code Review Assistant
```
1. Ask Claude: "Review this function"
2. Paste your code
3. Get voice feedback
```

### 5. Documentation Generation
```
1. Dictate documentation
2. Claude helps structure it
3. Export as markdown
```

### 6. Learning & Tutorials
```
1. Ask questions via voice
2. Get audio explanations
3. Save conversations
```

---

## 📋 Requirements

### System Requirements
- **Python:** 3.8 or higher
- **OS:** Linux, macOS, or Windows
- **RAM:** 4GB+ (8GB recommended for large Whisper models)
- **Storage:** 2GB+ for dependencies and models

### Required API Keys
- **Anthropic API Key** - Get from [console.anthropic.com](https://console.anthropic.com/)
- **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com/api-keys)

### Python Packages
See `deployment/requirements.txt` for complete list.

**Core:**
- anthropic
- openai
- pyyaml
- numpy

**Voice:**
- openai-whisper
- torch

**Web:**
- gradio
- aiohttp
- websockets

---

## 🎯 Next Steps

### If you're new:
1. Run `python quick_start.py`
2. Follow the setup instructions
3. Launch web interface
4. Try the examples

### If you're ready to code:
1. Check `examples/example_usage.py`
2. Read `USAGE_GUIDE.md`
3. Explore the API
4. Build something cool!

### If you're deploying:
1. Read deployment section in `USAGE_GUIDE.md`
2. Configure environment
3. Choose deployment method
4. Deploy!

---

## 🆘 Troubleshooting

### Installation Issues
```bash
# Verify Python version
python --version  # Should be 3.8+

# Install dependencies
pip install -r deployment/requirements.txt

# Test installation
python test_installation.py
```

### API Key Issues
```bash
# Check if keys are set
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY

# Set keys
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

### Server Issues
```bash
# Start bridge server first
python claude-bridge/bridge_server.py

# Then start web interface
python web-interface/app.py
```

For detailed troubleshooting, see **[USAGE_GUIDE.md](USAGE_GUIDE.md)** § Troubleshooting

---

## 📞 Support

1. **Check Documentation**
   - README.md (overview)
   - PROJECT_SUMMARY.md (details)
   - USAGE_GUIDE.md (how-to)

2. **Run Diagnostics**
   - `python test_installation.py`
   - `python quick_start.py`

3. **Review Examples**
   - `examples/example_usage.py`

4. **Check Configuration**
   - `config/settings.yaml`
   - Environment variables

---

## 🎓 Learn More

### Documentation Files
- **Overview:** PROJECT_SUMMARY.md
- **Usage:** USAGE_GUIDE.md
- **Examples:** examples/example_usage.py
- **Setup:** deployment/setup.py

### External Resources
- **Anthropic Docs:** https://docs.anthropic.com
- **OpenAI Whisper:** https://github.com/openai/whisper
- **Gradio:** https://gradio.app

---

## 📄 License

MIT License - Free for personal use

---

## 🎉 You're Ready!

This voice development wrapper is ready to enhance your productivity. Whether you're:

- 🎤 Dictating code
- 💬 Chatting with Claude
- 📝 Transcribing audio
- 🔊 Generating speech
- 🚀 Building voice apps

**Everything you need is here!**

### 👉 Start with:
```bash
python quick_start.py
```

Then choose your adventure:
- **Explore:** `python web-interface/app.py`
- **Learn:** `python examples/example_usage.py`
- **Build:** Read `USAGE_GUIDE.md`

---

**Questions?** Check the documentation!  
**Issues?** Run the test suite!  
**Ready?** Launch the web interface!

🎤 **Happy voice coding!** 🎤

---

*Last updated: November 2025*  
*Version: 1.0.0*  
*Status: Production Ready ✅*
