# Voice Development Wrapper - Usage Guide

## Quick Start

### 1. Installation

```bash
# Run the automated setup
python deployment/setup.py

# Or manual setup:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r deployment/requirements.txt
```

### 2. Configuration

Edit `config/settings.yaml` or set environment variables:

```bash
export ANTHROPIC_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"
```

### 3. Running the Services

#### Web Interface (Gradio)
```bash
python web-interface/app.py
```
Access at: http://localhost:7860

#### Voice Bridge Server
```bash
python claude-bridge/bridge_server.py
```
- HTTP API: http://localhost:8765
- WebSocket: ws://localhost:8766

#### VS Code Extension
1. Open VS Code
2. Install extension from `vscode-extension/`
3. Use `Ctrl+Shift+V` to activate voice mode

---

## Features & Usage

### 1. Voice Chat with Claude

**Web Interface:**
1. Navigate to the "Voice Chat" tab
2. Click "Record" and speak your question
3. Claude will respond with both text and voice

**API:**
```python
from claude_bridge.api_client import VoiceEnabledClaudeClient

client = VoiceEnabledClaudeClient()

# Record audio with your preferred method
import sounddevice as sd
import numpy as np

duration = 5  # seconds
sample_rate = 16000
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()

# Have a voice conversation
result = client.voice_conversation(audio.flatten())
print(f"You: {result['user_text']}")
print(f"Claude: {result['response_text']}")

# Play audio response
# (use your preferred audio playback library)
```

### 2. Speech-to-Text

**Web Interface:**
- Navigate to "Transcription" tab
- Upload audio file or record
- Click "Transcribe"

**API:**
```python
from core.voice_manager import VoiceManager

vm = VoiceManager()

# Transcribe audio file
text = vm.transcribe_file("your_audio.wav")
print(text)

# Transcribe numpy array
import numpy as np
audio_data = np.array([...])  # Your audio data
text = vm.listen(audio_data)
print(text)
```

**VS Code:**
1. Press `Ctrl+Shift+V` to start listening
2. Speak your code or text
3. Press again to stop and insert transcription

### 3. Text-to-Speech

**Web Interface:**
- Navigate to "Synthesis" tab
- Enter text and select voice
- Click "Synthesize"

**API:**
```python
from core.voice_manager import VoiceManager

vm = VoiceManager()

# Synthesize to file
vm.synthesize_to_file("Hello world!", "output.mp3")

# Get audio bytes
audio_bytes = vm.speak("Hello world!")

# Change voice
vm.change_voice("shimmer")
audio_bytes = vm.speak("Different voice!")
```

### 4. Text Chat with Claude

**Web Interface:**
- Navigate to "Text Chat" tab
- Type your message
- Get responses from Claude

**API:**
```python
from claude_bridge.api_client import ClaudeAPIClient

client = ClaudeAPIClient()

# Simple message
response = client.send_message("Explain Python decorators")
print(response)

# Streaming response
async for chunk in client.send_message_streaming("Write a poem"):
    print(chunk, end='', flush=True)

# With system prompt
response = client.send_message(
    "What's the weather like?",
    system_prompt="You are a helpful weather assistant"
)
```

---

## VS Code Extension

### Activation
The extension activates automatically when you open VS Code.

### Commands

| Command | Shortcut | Description |
|---------|----------|-------------|
| Toggle Voice Mode | `Ctrl+Shift+V` | Start/stop voice listening |
| Ask Claude | `Ctrl+Shift+C` | Ask Claude a question |
| Dictate Code | - | Start code dictation mode |

### Status Bar
- Shows voice status (Off/Listening/Processing)
- Click to toggle voice mode

### Configuration

Access via: Settings → Extensions → Voice Development Assistant

```json
{
  "voiceDev.serverUrl": "ws://localhost:8766",
  "voiceDev.autoTranscribe": true,
  "voiceDev.showTranscription": true
}
```

---

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8766');

ws.onopen = () => {
    console.log('Connected to voice server');
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
};
```

### Message Format

**Send Audio:**
```json
{
  "type": "audio",
  "audio": "base64_encoded_audio_data"
}
```

**Send Text:**
```json
{
  "type": "text",
  "text": "Your message here",
  "synthesize": true
}
```

**Responses:**
```json
{
  "type": "transcription",
  "text": "Transcribed text"
}
```
```json
{
  "type": "response_chunk",
  "text": "Part of Claude's response"
}
```
```json
{
  "type": "audio_response",
  "audio": "base64_encoded_audio",
  "text": "Complete response text"
}
```

---

## HTTP API Endpoints

Base URL: `http://localhost:8765`

### GET /health
Health check

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "stt": "whisper",
    "tts": "openai",
    "claude": "claude-sonnet-4-20250514"
  }
}
```

### POST /transcribe
Transcribe audio to text

**Request:**
```json
{
  "audio": "base64_encoded_audio"
}
```

**Response:**
```json
{
  "text": "Transcribed text"
}
```

### POST /synthesize
Convert text to speech

**Request:**
```json
{
  "text": "Text to synthesize"
}
```

**Response:**
```json
{
  "audio": "base64_encoded_audio"
}
```

### POST /conversation
Complete voice conversation

**Request:**
```json
{
  "audio": "base64_encoded_audio"
}
```

**Response:**
```json
{
  "user_text": "What you said",
  "response_text": "Claude's response",
  "audio_response": "base64_encoded_audio"
}
```

---

## Configuration Options

### STT Providers

**Whisper (Default):**
```yaml
stt:
  provider: "whisper"
  model: "base"  # tiny, base, small, medium, large
  language: "en"
```

**Browser Web Speech:**
```yaml
stt:
  provider: "browser"
```

**Deepgram:**
```yaml
stt:
  provider: "deepgram"
```

### TTS Providers

**OpenAI (Default):**
```yaml
tts:
  provider: "openai"
  voice: "nova"  # alloy, echo, fable, onyx, nova, shimmer
  speed: 1.0
  model: "tts-1"
```

**ElevenLabs:**
```yaml
tts:
  provider: "elevenlabs"
  voice: "your_voice_id"
```

**Coqui:**
```yaml
tts:
  provider: "coqui"
```

### Claude Settings

```yaml
claude:
  model: "claude-sonnet-4-20250514"
  max_tokens: 4096
  temperature: 1.0
  stream: true
```

---

## Deployment

### Hugging Face Spaces

1. Create a new Space on Hugging Face
2. Set secrets:
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY`
3. Push repository to Space:
```bash
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE
git push space main
```

4. Space will auto-deploy

### Docker

```bash
# Build image
docker build -t voice-dev-wrapper .

# Run container
docker run -p 7860:7860 -p 8765:8765 -p 8766:8766 \
  -e ANTHROPIC_API_KEY=your_key \
  -e OPENAI_API_KEY=your_key \
  voice-dev-wrapper
```

### Local Server

```bash
# Start all services
python claude-bridge/bridge_server.py &
python web-interface/app.py
```

---

## Troubleshooting

### Common Issues

**1. "Voice server not connected" in VS Code**
- Ensure bridge server is running: `python claude-bridge/bridge_server.py`
- Check server URL in VS Code settings

**2. "API key not configured"**
- Set environment variables or edit `config/settings.yaml`
- Ensure `.env` file exists and has correct keys

**3. Whisper model download fails**
- First run downloads model (~140MB for base)
- Ensure stable internet connection
- Use smaller model: `model: "tiny"`

**4. Audio quality issues**
- Check sample rate matches config (16000 Hz)
- Ensure audio is mono channel
- Try different Whisper model size

**5. Slow transcription**
- Use smaller Whisper model
- Consider GPU acceleration (requires `torch` with CUDA)
- Use Deepgram API for faster cloud-based STT

### Performance Tips

1. **For faster STT:**
   - Use `tiny` or `base` Whisper models
   - Consider Deepgram for real-time transcription

2. **For better accuracy:**
   - Use `medium` or `large` Whisper models
   - Ensure clear audio input (good microphone)

3. **For lower latency:**
   - Enable streaming mode
   - Use smaller chunk sizes

---

## Advanced Usage

### Custom Voice Commands

Add custom commands in VS Code extension:

```javascript
// In extension.js
vscode.commands.registerCommand('voice-dev.customCommand', async () => {
    // Your custom logic here
});
```

### Integration with Other Tools

**With Cursor IDE:**
```python
# Use the API client in Cursor's AI features
from claude_bridge.api_client import ClaudeAPIClient
client = ClaudeAPIClient()
```

**With Jupyter Notebooks:**
```python
from voice_manager import VoiceManager
vm = VoiceManager()

# Use in notebook cells
%%voice_input
# This would be a magic command you create
```

### Conversation Export/Import

```python
from claude_bridge.api_client import ClaudeAPIClient

client = ClaudeAPIClient()

# Export conversation
client.export_conversation("my_session.json")

# Import later
client.import_conversation("my_session.json")
```

---

## Support

For issues or questions:
1. Check troubleshooting section
2. Review configuration files
3. Check server logs
4. Open an issue on the repository

---

## License

MIT License - Personal use
