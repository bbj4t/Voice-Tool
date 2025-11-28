#!/usr/bin/env python3
"""
Voice Development Wrapper - Hugging Face Spaces Entry Point
Optimized for ZeroGPU H200 cluster
Uses OpenRouter for LLM and TTS access
"""

import gradio as gr
import numpy as np
import sys
import os
from pathlib import Path
import tempfile
import requests
import json

# Check Gradio version for compatibility
GRADIO_VERSION = tuple(map(int, gr.__version__.split(".")[:2]))
IS_GRADIO_4 = GRADIO_VERSION[0] == 4
print(f"📦 Gradio version: {gr.__version__} (v{GRADIO_VERSION[0]} mode)")

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
            'apis': {'openrouter_key': ''},
            'stt': {'provider': 'whisper', 'model': 'base', 'language': 'en', 'sample_rate': 16000},
            'tts': {'provider': 'huggingface', 'model': 'microsoft/speecht5_tts'},
            'llm': {'model': 'anthropic/claude-sonnet-4-20250514', 'max_tokens': 4096, 'temperature': 1.0}
        }
    
    # Override with environment variables
    config['apis']['openrouter_key'] = os.getenv('OPENROUTER_API_KEY', config['apis'].get('openrouter_key', ''))
    
    return config

config = load_config()

# OpenRouter API base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

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

# TTS Model (lazy loading) - uses HuggingFace models
tts_pipeline = None
tts_processor = None
tts_model = None

def get_tts_pipeline():
    """Get HuggingFace TTS pipeline"""
    global tts_pipeline, tts_processor, tts_model
    if tts_pipeline is None:
        try:
            import torch
            from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
            from datasets import load_dataset
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Loading TTS models on {device}...")
            
            # Load SpeechT5 models
            tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts").to(device)
            vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan").to(device)
            
            # Load speaker embeddings
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            speaker_embeddings = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0).to(device)
            
            tts_pipeline = {
                "processor": tts_processor,
                "model": tts_model,
                "vocoder": vocoder,
                "speaker_embeddings": speaker_embeddings,
                "device": device
            }
            print("✅ HuggingFace TTS initialized (SpeechT5)")
        except Exception as e:
            print(f"⚠️ SpeechT5 failed, trying alternative: {e}")
            try:
                # Fallback to a simpler TTS
                from transformers import pipeline
                tts_pipeline = pipeline("text-to-speech", model="facebook/mms-tts-eng")
                print("✅ HuggingFace TTS initialized (MMS-TTS)")
            except Exception as e2:
                print(f"❌ Error initializing TTS: {e2}")
                tts_pipeline = None
    return tts_pipeline

# Conversation history
conversation_history = []

def chat_with_openrouter(messages: list, model: str = None) -> str:
    """Send chat request to OpenRouter API"""
    api_key = config['apis']['openrouter_key']
    if not api_key:
        raise ValueError("OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable.")
    
    model = model or config.get('llm', {}).get('model', 'anthropic/claude-sonnet-4-20250514')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://huggingface.co/spaces",  # Required by OpenRouter
        "X-Title": "Voice Development Assistant"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": config.get('llm', {}).get('max_tokens', 4096),
        "temperature": config.get('llm', {}).get('temperature', 1.0)
    }
    
    response = requests.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    result = response.json()
    return result['choices'][0]['message']['content']


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


def synthesize_text(text, voice="default"):
    """Synthesize text to speech using HuggingFace TTS"""
    try:
        if not text:
            return None, "No text provided"
        
        import torch
        import scipy.io.wavfile as wavfile
        
        tts = get_tts_pipeline()
        if tts is None:
            return None, "TTS not available"
        
        # Check if it's a transformers pipeline or our custom dict
        if isinstance(tts, dict):
            # SpeechT5 model
            inputs = tts["processor"](text=text, return_tensors="pt").to(tts["device"])
            with torch.no_grad():
                speech = tts["model"].generate_speech(
                    inputs["input_ids"], 
                    tts["speaker_embeddings"], 
                    vocoder=tts["vocoder"]
                )
            audio_data = speech.cpu().numpy()
            sample_rate = 16000
        else:
            # MMS-TTS pipeline
            result = tts(text)
            audio_data = result["audio"][0]
            sample_rate = result["sampling_rate"]
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            wavfile.write(tmp.name, sample_rate, audio_data)
            tmp_path = tmp.name
        
        return tmp_path, f"✅ Synthesized {len(text)} characters"
    
    except Exception as e:
        return None, f"Error synthesizing: {str(e)}"


def chat_with_claude(message, history):
    """Chat with LLM via OpenRouter"""
    global conversation_history
    
    try:
        if not message.strip():
            return history
        
        # Build messages
        conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Call OpenRouter
        assistant_message = chat_with_openrouter(conversation_history)
        
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
    """Complete voice conversation with LLM via OpenRouter"""
    try:
        if audio is None:
            return None, "No audio provided", ""
        
        sample_rate, audio_data = audio
        
        # Transcribe
        user_text = transcribe_with_gpu(audio_data)
        if not user_text:
            return None, "No speech detected", ""
        
        # Get LLM response via OpenRouter
        global conversation_history
        
        conversation_history.append({"role": "user", "content": user_text})
        
        response_text = chat_with_openrouter(conversation_history)
        
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Synthesize response
        audio_path, _ = synthesize_text(response_text)
        
        conversation_log = f"**🎤 You:** {user_text}\n\n**🤖 Assistant:** {response_text}"
        
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
    openrouter_ok = bool(config['apis'].get('openrouter_key'))
    
    status = []
    if openrouter_ok:
        status.append("✅ OpenRouter API key configured (LLM)")
    else:
        status.append("❌ OpenRouter API key missing (Set OPENROUTER_API_KEY)")
    
    status.append("✅ HuggingFace TTS (free, no API key needed)")
    
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
                    # Gradio 4.x uses 'sources' parameter, Gradio 6.x also supports it
                    voice_input = gr.Audio(
                        sources=["microphone"] if not IS_GRADIO_4 else ["microphone"],
                        type="numpy",
                        label="🎙️ Click to Record"
                    )
                    voice_submit = gr.Button("🚀 Send to Claude", variant="primary")
                
                with gr.Column(scale=1):
                    voice_output = gr.Audio(label="🔊 Claude's Response")
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
                        lines=8
                    )
            
            stt_btn.click(transcribe_audio, inputs=[stt_input], outputs=[stt_output])
        
        # TTS Tab
        with gr.Tab("🔊 Speak"):
            gr.Markdown("### Convert text to natural speech (HuggingFace TTS)")
            
            with gr.Row():
                with gr.Column():
                    tts_input = gr.Textbox(
                        label="Text to Speak",
                        lines=5
                    )
                    tts_btn = gr.Button("🔊 Generate Speech", variant="primary")
                
                with gr.Column():
                    tts_output = gr.Audio(label="Generated Audio")
                    tts_status = gr.Textbox(label="Status", interactive=False)
            
            tts_btn.click(synthesize_text, inputs=[tts_input], outputs=[tts_output, tts_status])
        
        # Text Chat Tab
        with gr.Tab("💬 Text Chat"):
            gr.Markdown("### Chat with Claude via text")
            
            chatbot = gr.Chatbot(height=400)
            
            with gr.Row():
                chat_input = gr.Textbox(
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
