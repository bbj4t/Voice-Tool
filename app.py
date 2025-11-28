#!/usr/bin/env python3
"""
Voice Development Wrapper - Hugging Face Spaces Entry Point
Optimized for ZeroGPU H200 cluster
"""

import gradio as gr
import numpy as np
import sys
import os
from pathlib import Path
import tempfile

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "core"))
sys.path.insert(0, str(Path(__file__).parent / "claude-bridge"))

# Check for ZeroGPU availability
try:
    import spaces
    ZERO_GPU_AVAILABLE = True
    print("🚀 ZeroGPU detected - GPU acceleration enabled!")
except ImportError:
    ZERO_GPU_AVAILABLE = False
    print("⚠️ ZeroGPU not available - running on CPU")

# Load configuration
def load_config():
    """Load configuration with environment variable overrides"""
    import yaml
    config_path = Path(__file__).parent / "config" / "settings.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        # Default configuration
        config = {
            'apis': {'openai_key': '', 'anthropic_key': ''},
            'stt': {'provider': 'whisper', 'model': 'base', 'language': 'en', 'sample_rate': 16000},
            'tts': {'provider': 'openai', 'voice': 'nova', 'speed': 1.0, 'model': 'tts-1'},
            'claude': {'model': 'claude-sonnet-4-20250514', 'max_tokens': 4096, 'temperature': 1.0, 'stream': True}
        }
    
    # Override with environment variables
    config['apis']['openai_key'] = os.getenv('OPENAI_API_KEY', config['apis'].get('openai_key', ''))
    config['apis']['anthropic_key'] = os.getenv('ANTHROPIC_API_KEY', config['apis'].get('anthropic_key', ''))
    
    return config

config = load_config()

# Initialize Whisper model (lazy loading for ZeroGPU)
whisper_model = None

def get_whisper_model():
    """Load Whisper model (uses GPU when available via ZeroGPU)"""
    global whisper_model
    if whisper_model is None:
        try:
            import whisper
            import torch
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model_name = config['stt'].get('model', 'base')
            
            print(f"Loading Whisper model '{model_name}' on {device}...")
            whisper_model = whisper.load_model(model_name, device=device)
            print(f"✅ Whisper model loaded on {device}")
        except Exception as e:
            print(f"❌ Error loading Whisper: {e}")
            raise
    return whisper_model

# TTS Client (lazy loading)
openai_client = None

def get_openai_client():
    """Get OpenAI client for TTS"""
    global openai_client
    if openai_client is None:
        try:
            from openai import OpenAI
            api_key = config['apis']['openai_key']
            if not api_key:
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            openai_client = OpenAI(api_key=api_key)
            print("✅ OpenAI client initialized")
        except Exception as e:
            print(f"❌ Error initializing OpenAI: {e}")
            raise
    return openai_client

# Claude Client (lazy loading)
claude_client = None
conversation_history = []

def get_claude_client():
    """Get Claude client"""
    global claude_client
    if claude_client is None:
        try:
            from anthropic import Anthropic
            api_key = config['apis']['anthropic_key']
            if not api_key:
                raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
            claude_client = Anthropic(api_key=api_key)
            print("✅ Claude client initialized")
        except Exception as e:
            print(f"❌ Error initializing Claude: {e}")
            raise
    return claude_client


# Define GPU-accelerated transcription function
def transcribe_audio_gpu(audio_data: np.ndarray) -> str:
    """Transcribe audio using Whisper (GPU accelerated when available)"""
    model = get_whisper_model()
    
    # Ensure audio is float32 and normalized
    if audio_data.dtype != np.float32:
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        else:
            audio_data = audio_data.astype(np.float32)
    
    # Handle stereo by taking first channel
    if len(audio_data.shape) > 1:
        audio_data = audio_data[:, 0] if audio_data.shape[1] > 1 else audio_data.flatten()
    
    result = model.transcribe(
        audio_data,
        language=config['stt'].get('language', 'en'),
        fp16=False  # Use FP32 for better compatibility
    )
    return result["text"].strip()


# Wrap with ZeroGPU decorator if available
if ZERO_GPU_AVAILABLE:
    @spaces.GPU(duration=60)
    def transcribe_with_gpu(audio_data: np.ndarray) -> str:
        """GPU-accelerated transcription with ZeroGPU"""
        return transcribe_audio_gpu(audio_data)
else:
    transcribe_with_gpu = transcribe_audio_gpu


def transcribe_audio(audio):
    """Transcribe audio input from Gradio"""
    try:
        if audio is None:
            return "No audio provided. Please record or upload audio."
        
        # Gradio returns (sample_rate, audio_data)
        sample_rate, audio_data = audio
        
        # Transcribe
        text = transcribe_with_gpu(audio_data)
        return text if text else "No speech detected."
    
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"


def synthesize_text(text, voice="nova"):
    """Synthesize text to speech using OpenAI TTS"""
    try:
        if not text:
            return None, "No text provided"
        
        client = get_openai_client()
        
        response = client.audio.speech.create(
            model=config['tts'].get('model', 'tts-1'),
            voice=voice,
            input=text,
            speed=config['tts'].get('speed', 1.0)
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        return tmp_path, f"✅ Synthesized {len(text)} characters with voice '{voice}'"
    
    except Exception as e:
        return None, f"Error synthesizing: {str(e)}"


def chat_with_claude(message, history):
    """Chat with Claude"""
    global conversation_history
    
    try:
        if not message.strip():
            return history
        
        client = get_claude_client()
        
        # Build messages
        conversation_history.append({
            "role": "user",
            "content": message
        })
        
        response = client.messages.create(
            model=config['claude'].get('model', 'claude-sonnet-4-20250514'),
            max_tokens=config['claude'].get('max_tokens', 4096),
            messages=conversation_history
        )
        
        assistant_message = response.content[0].text
        
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        history.append([message, assistant_message])
        return history
    
    except Exception as e:
        history.append([message, f"Error: {str(e)}"])
        return history


def voice_chat(audio):
    """Complete voice conversation with Claude"""
    try:
        if audio is None:
            return None, "No audio provided", ""
        
        sample_rate, audio_data = audio
        
        # Transcribe
        user_text = transcribe_with_gpu(audio_data)
        if not user_text:
            return None, "No speech detected", ""
        
        # Get Claude's response
        client = get_claude_client()
        global conversation_history
        
        conversation_history.append({"role": "user", "content": user_text})
        
        response = client.messages.create(
            model=config['claude'].get('model', 'claude-sonnet-4-20250514'),
            max_tokens=config['claude'].get('max_tokens', 4096),
            messages=conversation_history
        )
        
        response_text = response.content[0].text
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Synthesize response
        audio_path, _ = synthesize_text(response_text)
        
        conversation_log = f"**🎤 You:** {user_text}\n\n**🤖 Claude:** {response_text}"
        
        return audio_path, conversation_log, response_text
    
    except Exception as e:
        return None, f"Error: {str(e)}", ""


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return []


# Check API keys status
def check_api_status():
    """Check if API keys are configured"""
    openai_ok = bool(config['apis'].get('openai_key'))
    anthropic_ok = bool(config['apis'].get('anthropic_key'))
    
    status = []
    if openai_ok:
        status.append("✅ OpenAI API key configured")
    else:
        status.append("❌ OpenAI API key missing (Set OPENAI_API_KEY)")
    
    if anthropic_ok:
        status.append("✅ Anthropic API key configured")
    else:
        status.append("❌ Anthropic API key missing (Set ANTHROPIC_API_KEY)")
    
    if ZERO_GPU_AVAILABLE:
        status.append("🚀 ZeroGPU enabled (H200 acceleration)")
    else:
        status.append("💻 Running on CPU")
    
    return "\n".join(status)


# Build Gradio Interface - version-agnostic approach
demo = gr.Blocks(title="🎤 Voice Development Assistant")

with demo:
    
    gr.Markdown("""
    # 🎤 Voice Development Assistant
    
    **Personal Voice Interface for Development Workflows**
    
    Speech-to-Text • Text-to-Speech • Claude AI Conversations
    """)
    
    # API Status
    with gr.Accordion("📊 System Status", open=False):
        status_display = gr.Markdown(check_api_status())
        refresh_btn = gr.Button("🔄 Refresh Status")
        refresh_btn.click(check_api_status, outputs=[status_display])
    
    with gr.Tabs():
        # Voice Chat Tab
        with gr.Tab("🎤 Voice Chat"):
            gr.Markdown("### Speak with Claude using your voice")
            
            with gr.Row():
                with gr.Column(scale=1):
                    voice_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="🎙️ Click to Record"
                    )
                    voice_submit = gr.Button("🚀 Send to Claude", variant="primary")
                
                with gr.Column(scale=1):
                    voice_output = gr.Audio(label="🔊 Claude's Response", type="filepath")
                    voice_log = gr.Markdown(label="Conversation")
                    voice_text = gr.Textbox(label="Response Text", lines=3, interactive=False)
            
            voice_submit.click(
                voice_chat,
                inputs=[voice_input],
                outputs=[voice_output, voice_log, voice_text]
            )
        
        # Transcription Tab
        with gr.Tab("📝 Transcribe"):
            gr.Markdown("### Convert speech to text using Whisper")
            
            with gr.Row():
                with gr.Column():
                    stt_input = gr.Audio(
                        sources=["microphone", "upload"],
                        type="numpy",
                        label="🎙️ Audio Input"
                    )
                    stt_btn = gr.Button("📝 Transcribe", variant="primary")
                
                with gr.Column():
                    stt_output = gr.Textbox(
                        label="Transcription",
                        lines=8,
                        placeholder="Transcribed text appears here..."
                    )
            
            stt_btn.click(transcribe_audio, inputs=[stt_input], outputs=[stt_output])
        
        # TTS Tab
        with gr.Tab("🔊 Speak"):
            gr.Markdown("### Convert text to natural speech")
            
            with gr.Row():
                with gr.Column():
                    tts_input = gr.Textbox(
                        label="Text to Speak",
                        lines=5,
                        placeholder="Enter text to synthesize..."
                    )
                    tts_voice = gr.Dropdown(
                        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        value="nova",
                        label="🎭 Voice"
                    )
                    tts_btn = gr.Button("🔊 Generate Speech", variant="primary")
                
                with gr.Column():
                    tts_output = gr.Audio(label="Generated Audio", type="filepath")
                    tts_status = gr.Textbox(label="Status", interactive=False)
            
            tts_btn.click(synthesize_text, inputs=[tts_input, tts_voice], outputs=[tts_output, tts_status])
        
        # Text Chat Tab
        with gr.Tab("💬 Text Chat"):
            gr.Markdown("### Chat with Claude via text")
            
            chatbot = gr.Chatbot(height=450)
            
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Type your message...",
                    label="Message",
                    scale=4
                )
                chat_submit = gr.Button("Send", variant="primary", scale=1)
            
            clear_btn = gr.Button("🗑️ Clear History")
            
            chat_submit.click(
                chat_with_claude,
                inputs=[chat_input, chatbot],
                outputs=[chatbot]
            ).then(lambda: "", outputs=[chat_input])
            
            chat_input.submit(
                chat_with_claude,
                inputs=[chat_input, chatbot],
                outputs=[chatbot]
            ).then(lambda: "", outputs=[chat_input])
            
            clear_btn.click(clear_history, outputs=[chatbot])
    
    gr.Markdown("""
    ---
    **Voice Development Assistant** • Built with Whisper, OpenAI TTS, and Claude
    
    🔐 Configure API keys as Hugging Face Space secrets or environment variables
    """)


# Launch
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
