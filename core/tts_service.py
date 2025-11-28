"""
Text-to-Speech Service
Provides voice synthesis using various TTS providers
"""

import asyncio
import os
from typing import Optional
import yaml
from pathlib import Path
import io

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


class TTSService:
    """Text-to-Speech service with multiple provider support"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config['tts']['provider']
        self.voice = config['tts']['voice']
        self.speed = config['tts']['speed']
        self.model = config['tts']['model']
        self.client = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected TTS provider"""
        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "elevenlabs":
            self._init_elevenlabs()
        elif self.provider == "coqui":
            self._init_coqui()
        elif self.provider == "browser":
            self._init_browser()
        else:
            raise ValueError(f"Unsupported TTS provider: {self.provider}")
    
    def _init_openai(self):
        """Initialize OpenAI TTS"""
        try:
            from openai import OpenAI
            api_key = config['apis']['openai_key'] or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            self.client = OpenAI(api_key=api_key)
            print("OpenAI TTS initialized")
        except ImportError:
            print("OpenAI SDK not installed. Install with: pip install openai")
            raise
    
    def _init_elevenlabs(self):
        """Initialize ElevenLabs TTS"""
        try:
            from elevenlabs import set_api_key
            api_key = os.getenv('ELEVENLABS_API_KEY')
            if not api_key:
                raise ValueError("ElevenLabs API key not configured")
            set_api_key(api_key)
            print("ElevenLabs TTS initialized")
        except ImportError:
            print("ElevenLabs SDK not installed. Install with: pip install elevenlabs")
            raise
    
    def _init_coqui(self):
        """Initialize Coqui TTS"""
        try:
            from TTS.api import TTS
            self.client = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
            print("Coqui TTS initialized")
        except ImportError:
            print("Coqui TTS not installed. Install with: pip install TTS")
            raise
    
    def _init_browser(self):
        """Initialize browser-based Web Speech API"""
        print("Browser TTS requires client-side implementation")
        # This will be handled by the web interface
        pass
    
    def synthesize(self, text: str, output_path: Optional[str] = None) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            
        Returns:
            Audio data as bytes
        """
        if self.provider == "openai":
            return self._synthesize_openai(text, output_path)
        elif self.provider == "elevenlabs":
            return self._synthesize_elevenlabs(text, output_path)
        elif self.provider == "coqui":
            return self._synthesize_coqui(text, output_path)
        else:
            raise NotImplementedError(f"Synthesis not implemented for {self.provider}")
    
    def _synthesize_openai(self, text: str, output_path: Optional[str] = None) -> bytes:
        """Synthesize using OpenAI TTS"""
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed
        )
        
        audio_data = response.content
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
        
        return audio_data
    
    def _synthesize_elevenlabs(self, text: str, output_path: Optional[str] = None) -> bytes:
        """Synthesize using ElevenLabs"""
        from elevenlabs import generate, voices
        
        # Get first available voice if not specified
        available_voices = voices()
        voice_id = self.voice if self.voice else available_voices[0].voice_id
        
        audio = generate(
            text=text,
            voice=voice_id,
            model="eleven_monolingual_v1"
        )
        
        # Convert generator to bytes
        audio_data = b''.join(audio)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(audio_data)
        
        return audio_data
    
    def _synthesize_coqui(self, text: str, output_path: Optional[str] = None) -> bytes:
        """Synthesize using Coqui TTS"""
        if output_path:
            self.client.tts_to_file(text=text, file_path=output_path)
            with open(output_path, 'rb') as f:
                return f.read()
        else:
            # Generate to temporary file then read
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name
            
            self.client.tts_to_file(text=text, file_path=tmp_path)
            with open(tmp_path, 'rb') as f:
                audio_data = f.read()
            
            os.unlink(tmp_path)
            return audio_data
    
    async def stream_synthesis(self, text: str):
        """
        Stream TTS output for long text
        
        Args:
            text: Text to synthesize
            
        Yields:
            Audio chunks as bytes
        """
        # Split text into sentences for streaming
        sentences = text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
        
        for sentence in sentences:
            if sentence.strip():
                audio_chunk = self.synthesize(sentence.strip())
                yield audio_chunk
    
    def get_available_voices(self):
        """Get list of available voices for the current provider"""
        if self.provider == "openai":
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        elif self.provider == "elevenlabs":
            from elevenlabs import voices
            return [v.name for v in voices()]
        elif self.provider == "coqui":
            return ["default"]  # Coqui uses model-specific voices
        else:
            return []


# Example usage
if __name__ == "__main__":
    # Test the TTS service
    tts = TTSService()
    
    print("TTS Service initialized successfully")
    print(f"Provider: {tts.provider}")
    print(f"Voice: {tts.voice}")
    print(f"Available voices: {tts.get_available_voices()}")
    
    # Test synthesis
    # test_text = "Hello! This is a test of the text to speech system."
    # audio = tts.synthesize(test_text, "test_output.mp3")
    # print(f"Generated {len(audio)} bytes of audio")
