"""
Voice Development Wrapper - Web Interface
Gradio app for Hugging Face Spaces deployment
"""

import gradio as gr
import numpy as np
import sys
from pathlib import Path
import yaml
import os

# Add core modules to path
sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent.parent / "claude-bridge"))

from voice_manager import VoiceManager
from api_client import VoiceEnabledClaudeClient

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# Initialize voice-enabled Claude client
try:
    voice_client = VoiceEnabledClaudeClient()
    print("Voice client initialized successfully")
except Exception as e:
    print(f"Error initializing voice client: {e}")
    voice_client = None


def transcribe_audio(audio):
    """Transcribe audio input"""
    if not voice_client:
        return "Error: Voice client not initialized"
    
    try:
        if audio is None:
            return "No audio provided"
        
        # Gradio returns (sample_rate, audio_data)
        sample_rate, audio_data = audio
        
        # Convert to float32 and normalize
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Transcribe
        text = voice_client.voice.listen(audio_data)
        return text
    
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"


def synthesize_text(text, voice="nova"):
    """Synthesize text to speech"""
    if not voice_client:
        return None, "Error: Voice client not initialized"
    
    try:
        if not text:
            return None, "No text provided"
        
        # Change voice if different
        if voice != voice_client.voice.tts.voice:
            voice_client.voice.change_voice(voice)
        
        # Synthesize
        audio_bytes = voice_client.voice.speak(text)
        
        # Save to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        
        return tmp_path, f"Synthesized {len(text)} characters"
    
    except Exception as e:
        return None, f"Error synthesizing text: {str(e)}"


def voice_conversation(audio):
    """Complete voice conversation with Claude"""
    if not voice_client:
        return None, "Error: Voice client not initialized", ""
    
    try:
        if audio is None:
            return None, "No audio provided", ""
        
        # Gradio returns (sample_rate, audio_data)
        sample_rate, audio_data = audio
        
        # Convert to float32 and normalize
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        # Have voice conversation
        result = voice_client.voice_conversation(audio_data)
        
        # Save response audio to temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
            tmp.write(result['audio_response'])
            tmp_path = tmp.name
        
        conversation_log = f"**You:** {result['user_text']}\n\n**Claude:** {result['response_text']}"
        
        return tmp_path, conversation_log, result['response_text']
    
    except Exception as e:
        return None, f"Error in conversation: {str(e)}", ""


def text_conversation(text, history):
    """Text-based conversation with Claude"""
    if not voice_client:
        return history + [["Error", "Voice client not initialized"]]
    
    try:
        if not text:
            return history
        
        # Get Claude's response
        response = voice_client.send_message(text)
        
        # Update history
        history.append([text, response])
        
        return history
    
    except Exception as e:
        history.append([text, f"Error: {str(e)}"])
        return history


def clear_conversation():
    """Clear conversation history"""
    if voice_client:
        voice_client.clear_history()
    return []


# Create Gradio interface
with gr.Blocks(title="Voice Development Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎤 Voice Development Assistant
    
    Personal development tool with voice-enabled Claude integration
    
    ### Features:
    - 🎤 Speech-to-Text (Whisper)
    - 🔊 Text-to-Speech (OpenAI TTS)
    - 🤖 Claude Conversation
    - 💬 Text & Voice Chat
    """)
    
    with gr.Tabs():
        # Tab 1: Voice Conversation
        with gr.Tab("🎤 Voice Chat"):
            gr.Markdown("### Have a voice conversation with Claude")
            
            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="Speak to Claude"
                    )
                    submit_btn = gr.Button("Send", variant="primary")
                
                with gr.Column():
                    audio_output = gr.Audio(label="Claude's Response")
                    conversation_text = gr.Markdown()
                    response_text = gr.Textbox(label="Response Text", lines=5)
            
            submit_btn.click(
                voice_conversation,
                inputs=[audio_input],
                outputs=[audio_output, conversation_text, response_text]
            )
        
        # Tab 2: Speech-to-Text
        with gr.Tab("📝 Transcription"):
            gr.Markdown("### Transcribe your voice to text")
            
            with gr.Row():
                with gr.Column():
                    stt_audio = gr.Audio(
                        sources=["microphone", "upload"],
                        type="numpy",
                        label="Audio Input"
                    )
                    transcribe_btn = gr.Button("Transcribe", variant="primary")
                
                with gr.Column():
                    transcription_output = gr.Textbox(
                        label="Transcription",
                        lines=10,
                        placeholder="Your transcribed text will appear here..."
                    )
            
            transcribe_btn.click(
                transcribe_audio,
                inputs=[stt_audio],
                outputs=[transcription_output]
            )
        
        # Tab 3: Text-to-Speech
        with gr.Tab("🔊 Synthesis"):
            gr.Markdown("### Convert text to natural speech")
            
            with gr.Row():
                with gr.Column():
                    tts_text = gr.Textbox(
                        label="Text to Speak",
                        lines=5,
                        placeholder="Enter text to synthesize..."
                    )
                    voice_select = gr.Dropdown(
                        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                        value="nova",
                        label="Voice"
                    )
                    synthesize_btn = gr.Button("Synthesize", variant="primary")
                
                with gr.Column():
                    tts_audio_output = gr.Audio(label="Generated Speech")
                    tts_status = gr.Textbox(label="Status")
            
            synthesize_btn.click(
                synthesize_text,
                inputs=[tts_text, voice_select],
                outputs=[tts_audio_output, tts_status]
            )
        
        # Tab 4: Text Chat
        with gr.Tab("💬 Text Chat"):
            gr.Markdown("### Chat with Claude via text")
            
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(
                placeholder="Type your message...",
                label="Message"
            )
            
            with gr.Row():
                submit_text_btn = gr.Button("Send", variant="primary")
                clear_btn = gr.Button("Clear History")
            
            submit_text_btn.click(
                text_conversation,
                inputs=[msg, chatbot],
                outputs=[chatbot]
            ).then(
                lambda: "",
                None,
                [msg]
            )
            
            msg.submit(
                text_conversation,
                inputs=[msg, chatbot],
                outputs=[chatbot]
            ).then(
                lambda: "",
                None,
                [msg]
            )
            
            clear_btn.click(
                clear_conversation,
                outputs=[chatbot]
            )
    
    gr.Markdown("""
    ---
    ### About
    
    This is a personal development tool for voice-enabled coding and AI assistance.
    Built with Whisper, OpenAI TTS, and Claude.
    
    **Note:** Make sure to configure your API keys in the environment or config file.
    """)


if __name__ == "__main__":
    # Launch the app
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True for public sharing
    )
