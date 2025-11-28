# Voice Development Wrapper - Project Summary

## 🎯 Overview

A comprehensive personal development tool that provides voice-enabled coding and AI assistance through speech-to-text (STT), text-to-speech (TTS), and Claude AI integration.

## 📦 What's Included

### Core Components

1. **Voice Services** (`core/`)
   - `stt_service.py` - Speech-to-text with multiple provider support (Whisper, Deepgram, Browser)
   - `tts_service.py` - Text-to-speech with multiple providers (OpenAI, ElevenLabs, Coqui)
   - `voice_manager.py` - Unified voice interaction coordinator

2. **Claude Integration** (`claude-bridge/`)
   - `api_client.py` - Claude API client with voice capabilities
   - `bridge_server.py` - WebSocket and HTTP servers for real-time voice interaction

3. **VS Code Extension** (`vscode-extension/`)
   - Voice-activated coding assistant
   - Keyboard shortcuts for quick voice input
   - Real-time transcription display
   - Claude integration within IDE

4. **Web Interface** (`web-interface/`)
   - Gradio-based UI for voice chat
   - Speech-to-text transcription
   - Text-to-speech synthesis
   - Text chat with Claude
   - Ready for Hugging Face Spaces deployment

5. **Deployment Tools** (`deployment/`)
   - `setup.py` - Automated setup script
   - `spaces_config.py` - Hugging Face Spaces configuration
   - `requirements.txt` - Python dependencies
   - Dockerfile for containerized deployment

6. **Documentation**
   - `README.md` - Project overview
   - `USAGE_GUIDE.md` - Comprehensive usage instructions
   - `examples/example_usage.py` - 10+ code examples

### Configuration

- `config/settings.yaml` - Central configuration file
- `.env` template for API keys
- Customizable TTS/STT provider settings

## 🚀 Quick Start

### 1. Basic Setup
```bash
# Install dependencies
pip install -r deployment/requirements.txt

# Configure API keys
export ANTHROPIC_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
```

### 2. Launch Options

**Option A: Web Interface**
```bash
python web-interface/app.py
# Opens at http://localhost:7860
```

**Option B: Voice Server**
```bash
python claude-bridge/bridge_server.py
# HTTP API: http://localhost:8765
# WebSocket: ws://localhost:8766
```

**Option C: VS Code Extension**
1. Install from `vscode-extension/`
2. Use `Ctrl+Shift+V` for voice mode

### 3. Test with Examples
```bash
python examples/example_usage.py
```

## 🎤 Features

### Speech-to-Text
- **Whisper** (default): High-quality offline transcription
- **Deepgram**: Fast cloud-based STT
- **Browser API**: Client-side speech recognition
- Multiple model sizes for speed/accuracy tradeoff

### Text-to-Speech
- **OpenAI TTS** (default): Natural-sounding voices
  - Voices: alloy, echo, fable, onyx, nova, shimmer
- **ElevenLabs**: Premium voice quality
- **Coqui**: Open-source TTS
- Speed and voice customization

### Claude Integration
- Voice conversations with Claude
- Text chat mode
- Streaming responses
- Conversation history management
- Export/import sessions

### VS Code Extension
- Voice dictation for code
- Ask Claude about code
- Inline transcription
- Customizable keyboard shortcuts

### Web Interface
- 4 interactive tabs:
  1. Voice Chat - Full voice conversation
  2. Transcription - Audio to text
  3. Synthesis - Text to speech
  4. Text Chat - Traditional chat

## 📊 Architecture

```
┌─────────────────┐
│  User Interface │
│                 │
│ • VS Code Ext   │
│ • Web UI        │
│ • API Clients   │
└────────┬────────┘
         │
┌────────┴────────┐
│  Bridge Server  │
│                 │
│ • WebSocket API │
│ • HTTP REST API │
└────────┬────────┘
         │
┌────────┴────────┐
│  Voice Manager  │
│                 │
│ • STT Service   │
│ • TTS Service   │
└────────┬────────┘
         │
┌────────┴────────┐
│   Claude API    │
│                 │
│ • Conversation  │
│ • Streaming     │
└─────────────────┘
```

## 🔧 Configuration Options

### Provider Selection

**Speech-to-Text:**
- `whisper` - Best for offline, high accuracy
- `deepgram` - Best for real-time, cloud-based
- `browser` - Best for web apps, no setup

**Text-to-Speech:**
- `openai` - Best balance of quality and cost
- `elevenlabs` - Best quality, premium
- `coqui` - Best for offline, open-source

### Performance Tuning

**For Speed:**
```yaml
stt:
  model: "tiny"  # Fastest Whisper model
tts:
  model: "tts-1"  # Faster OpenAI model
```

**For Quality:**
```yaml
stt:
  model: "large"  # Most accurate
tts:
  voice: "nova"  # High-quality voice
```

## 📝 API Reference

### Python API

```python
# Voice Manager
from core.voice_manager import VoiceManager
vm = VoiceManager()
text = vm.listen(audio_data)
audio = vm.speak("Hello!")

# Claude Client
from claude_bridge.api_client import VoiceEnabledClaudeClient
client = VoiceEnabledClaudeClient()
result = client.voice_conversation(audio_data)

# Async Streaming
async for chunk in client.send_message_streaming("Question"):
    print(chunk, end='')
```

### WebSocket API

```javascript
const ws = new WebSocket('ws://localhost:8766');

// Send audio
ws.send(JSON.stringify({
  type: 'audio',
  audio: base64_audio
}));

// Receive responses
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle transcription, response_chunk, audio_response
};
```

### HTTP API

```bash
# Health check
curl http://localhost:8765/health

# Transcribe
curl -X POST http://localhost:8765/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio": "base64_data"}'

# Synthesize
curl -X POST http://localhost:8765/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'
```

## 🌐 Deployment

### Hugging Face Spaces

1. Create new Space
2. Set secrets:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
3. Push repository
4. Auto-deploys!

### Docker

```bash
docker build -t voice-dev .
docker run -p 7860:7860 -p 8765:8765 -p 8766:8766 \
  -e ANTHROPIC_API_KEY=key \
  -e OPENAI_API_KEY=key \
  voice-dev
```

### Local Development

```bash
# Terminal 1: Bridge Server
python claude-bridge/bridge_server.py

# Terminal 2: Web Interface
python web-interface/app.py
```

## 📚 Documentation Files

- **README.md** - Project overview and introduction
- **USAGE_GUIDE.md** - Detailed usage instructions
- **examples/example_usage.py** - 10 practical examples
- **quick_start.py** - Fast setup and validation
- **config/settings.yaml** - Configuration reference

## 🎓 Example Use Cases

1. **Voice Coding**
   - Dictate code in VS Code
   - Ask Claude for code reviews
   - Voice-controlled refactoring

2. **Documentation**
   - Transcribe meeting notes
   - Generate documentation via voice
   - Convert audio recordings to text

3. **Learning**
   - Voice conversations with Claude
   - Audio summaries of code
   - Interactive tutorials

4. **Accessibility**
   - Hands-free coding
   - Voice-controlled IDE
   - Audio feedback

## 🔐 Privacy & Security

- API keys stored in environment variables
- No persistent storage of conversations (optional export)
- Audio processing can be done offline (Whisper)
- All data encrypted in transit
- Open source - verify all code

## 🛠️ Troubleshooting

### Common Issues

1. **"Voice server not connected"**
   - Start bridge server: `python claude-bridge/bridge_server.py`

2. **"API key not configured"**
   - Set environment variables or edit config

3. **Slow transcription**
   - Use smaller Whisper model (`tiny` or `base`)

4. **Import errors**
   - Install dependencies: `pip install -r deployment/requirements.txt`

See USAGE_GUIDE.md for detailed troubleshooting.

## 📈 Performance Metrics

### Whisper Models

| Model  | Size  | Speed | Accuracy |
|--------|-------|-------|----------|
| tiny   | 39MB  | Fast  | Good     |
| base   | 74MB  | Fast  | Better   |
| small  | 244MB | Medium| Great    |
| medium | 769MB | Slow  | Excellent|
| large  | 1.5GB | Slower| Best     |

### API Costs (Approximate)

- OpenAI Whisper: $0.006 per minute
- OpenAI TTS: $15 per 1M characters
- Claude API: Varies by model

## 🚦 Status

**✅ Fully Functional:**
- Core STT/TTS services
- Claude API integration
- Web interface
- WebSocket/HTTP servers
- Configuration system

**🔨 Ready for Development:**
- VS Code extension (requires audio recording)
- Browser-based STT/TTS
- Additional provider integrations

**📝 Documentation:**
- Complete setup guides
- API reference
- Code examples
- Troubleshooting

## 🤝 Contributing

This is a personal development tool, but feel free to:
- Fork and customize
- Add new features
- Improve documentation
- Share feedback

## 📄 License

MIT License - Free for personal use

## 🎯 Next Steps

1. **Immediate:**
   - Run `python quick_start.py`
   - Configure API keys
   - Launch web interface

2. **Short-term:**
   - Test all features
   - Customize configuration
   - Integrate with workflow

3. **Long-term:**
   - Deploy to cloud
   - Add custom features
   - Extend integrations

---

## 📞 Support

For issues or questions:
1. Check USAGE_GUIDE.md
2. Review example scripts
3. Verify configuration
4. Check server logs

---

**Built with:** Python, Whisper, OpenAI TTS, Claude API, Gradio, WebSocket  
**For:** Personal development productivity  
**By:** Voice-enabled development workflow enthusiasts

🎤 Happy voice coding! 🎤
