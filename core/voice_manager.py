"""
Voice Manager
Coordinates TTS and STT services for seamless voice interaction
"""

import asyncio
import numpy as np
from typing import Optional, Callable
import yaml
from pathlib import Path
from queue import Queue
import threading

from stt_service import STTService
from tts_service import TTSService

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


class VoiceManager:
    """Main voice interaction manager"""
    
    def __init__(self):
        self.stt = STTService()
        self.tts = TTSService()
        self.is_listening = False
        self.is_speaking = False
        self.audio_queue = Queue()
        self.transcription_callback = None
        self.synthesis_callback = None
        
        print("Voice Manager initialized")
        print(f"STT Provider: {self.stt.provider}")
        print(f"TTS Provider: {self.tts.provider}")
    
    def set_transcription_callback(self, callback: Callable[[str], None]):
        """Set callback function for transcription results"""
        self.transcription_callback = callback
    
    def set_synthesis_callback(self, callback: Callable[[bytes], None]):
        """Set callback function for synthesized audio"""
        self.synthesis_callback = callback
    
    def listen(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio input
        
        Args:
            audio_data: Audio samples as NumPy array
            
        Returns:
            Transcribed text
        """
        self.is_listening = True
        try:
            text = self.stt.transcribe_audio(audio_data)
            if self.transcription_callback:
                self.transcription_callback(text)
            return text
        finally:
            self.is_listening = False
    
    def speak(self, text: str, save_to: Optional[str] = None) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to speak
            save_to: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        self.is_speaking = True
        try:
            audio_data = self.tts.synthesize(text, save_to)
            if self.synthesis_callback:
                self.synthesis_callback(audio_data)
            return audio_data
        finally:
            self.is_speaking = False
    
    async def conversation_loop(
        self,
        message_handler: Callable[[str], str],
        audio_input_stream,
        audio_output_callback: Callable[[bytes], None]
    ):
        """
        Run a continuous voice conversation loop
        
        Args:
            message_handler: Function that takes transcribed text and returns response
            audio_input_stream: Async iterator of audio chunks
            audio_output_callback: Function to play audio output
        """
        print("Starting conversation loop...")
        
        def on_transcription(text: str):
            """Handle transcribed text"""
            print(f"You: {text}")
            
            # Get response from message handler
            response = message_handler(text)
            print(f"Assistant: {response}")
            
            # Synthesize and play response
            audio = self.speak(response)
            audio_output_callback(audio)
        
        # Set up transcription callback
        self.set_transcription_callback(on_transcription)
        
        # Stream transcription
        await self.stt.stream_transcription(audio_input_stream, on_transcription)
    
    async def speak_streaming(self, text: str):
        """
        Speak long text with streaming output
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks as bytes
        """
        async for audio_chunk in self.tts.stream_synthesis(text):
            if self.synthesis_callback:
                self.synthesis_callback(audio_chunk)
            yield audio_chunk
    
    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        return self.stt.transcribe_file(file_path)
    
    def synthesize_to_file(self, text: str, output_path: str):
        """
        Synthesize text and save to file
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
        """
        self.tts.synthesize(text, output_path)
    
    def get_status(self) -> dict:
        """Get current status of voice manager"""
        return {
            "stt_provider": self.stt.provider,
            "tts_provider": self.tts.provider,
            "is_listening": self.is_listening,
            "is_speaking": self.is_speaking,
            "available_voices": self.tts.get_available_voices()
        }
    
    def change_voice(self, voice: str):
        """Change TTS voice"""
        self.tts.voice = voice
        print(f"Voice changed to: {voice}")
    
    def change_stt_model(self, model: str):
        """Change STT model"""
        self.stt.model_name = model
        self.stt._initialize_provider()
        print(f"STT model changed to: {model}")


# Example usage and testing
if __name__ == "__main__":
    vm = VoiceManager()
    
    print("\nVoice Manager Status:")
    print(vm.get_status())
    
    # Example: Transcribe and speak
    # text = "Hello, this is a test of the voice manager system."
    # audio = vm.speak(text, "test_voice.mp3")
    # print(f"Generated {len(audio)} bytes of audio")
    
    # Example: Transcribe a file
    # transcription = vm.transcribe_file("input_audio.wav")
    # print(f"Transcription: {transcription}")
