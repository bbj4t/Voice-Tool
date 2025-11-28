"""
Speech-to-Text Service
Provides real-time transcription using various STT providers
"""

import asyncio
import numpy as np
from typing import Optional, Callable
import yaml
import os
from pathlib import Path

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


class STTService:
    """Speech-to-Text service with multiple provider support"""
    
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config['stt']['provider']
        self.model_name = config['stt']['model']
        self.language = config['stt']['language']
        self.sample_rate = config['stt']['sample_rate']
        self.model = None
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the selected STT provider"""
        if self.provider == "whisper":
            self._init_whisper()
        elif self.provider == "browser":
            self._init_browser()
        elif self.provider == "deepgram":
            self._init_deepgram()
        else:
            raise ValueError(f"Unsupported STT provider: {self.provider}")
    
    def _init_whisper(self):
        """Initialize OpenAI Whisper model"""
        try:
            import whisper
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            print("Whisper model loaded successfully")
        except ImportError:
            print("Whisper not installed. Install with: pip install openai-whisper")
            raise
    
    def _init_browser(self):
        """Initialize browser-based Web Speech API"""
        print("Browser STT requires client-side implementation")
        # This will be handled by the web interface
        pass
    
    def _init_deepgram(self):
        """Initialize Deepgram API"""
        try:
            from deepgram import Deepgram
            api_key = os.getenv('DEEPGRAM_API_KEY')
            self.model = Deepgram(api_key)
            print("Deepgram initialized")
        except ImportError:
            print("Deepgram SDK not installed. Install with: pip install deepgram-sdk")
            raise
    
    def transcribe_audio(self, audio_data: np.ndarray) -> str:
        """
        Transcribe audio data to text
        
        Args:
            audio_data: NumPy array of audio samples
            
        Returns:
            Transcribed text string
        """
        if self.provider == "whisper":
            return self._transcribe_whisper(audio_data)
        elif self.provider == "deepgram":
            return self._transcribe_deepgram(audio_data)
        else:
            raise NotImplementedError(f"Transcription not implemented for {self.provider}")
    
    def _transcribe_whisper(self, audio_data: np.ndarray) -> str:
        """Transcribe using Whisper"""
        # Ensure audio is float32 and normalized
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32) / 32768.0
        
        result = self.model.transcribe(
            audio_data,
            language=self.language,
            fp16=False  # Use FP32 for CPU
        )
        return result["text"].strip()
    
    async def _transcribe_deepgram(self, audio_data: np.ndarray) -> str:
        """Transcribe using Deepgram API"""
        # Convert audio to bytes
        audio_bytes = (audio_data * 32768).astype(np.int16).tobytes()
        
        source = {'buffer': audio_bytes, 'mimetype': 'audio/wav'}
        response = await self.model.transcription.prerecorded(
            source,
            {'punctuate': True, 'language': self.language}
        )
        
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcript.strip()
    
    async def stream_transcription(
        self, 
        audio_stream, 
        callback: Callable[[str], None]
    ):
        """
        Stream audio and provide real-time transcription
        
        Args:
            audio_stream: Async iterator of audio chunks
            callback: Function to call with each transcription result
        """
        buffer = []
        chunk_size = self.sample_rate * config['stt']['chunk_duration_ms'] // 1000
        
        async for chunk in audio_stream:
            buffer.append(chunk)
            
            # When we have enough audio, transcribe
            if len(buffer) * len(chunk) >= chunk_size:
                audio_data = np.concatenate(buffer)
                buffer = []
                
                try:
                    text = self.transcribe_audio(audio_data)
                    if text:
                        callback(text)
                except Exception as e:
                    print(f"Transcription error: {e}")
    
    def transcribe_file(self, file_path: str) -> str:
        """
        Transcribe an audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if self.provider == "whisper":
            result = self.model.transcribe(file_path, language=self.language)
            return result["text"].strip()
        else:
            raise NotImplementedError(f"File transcription not implemented for {self.provider}")


# Example usage
if __name__ == "__main__":
    # Test the STT service
    stt = STTService()
    
    # Test with a sample audio file (you'll need to provide one)
    # text = stt.transcribe_file("test_audio.wav")
    # print(f"Transcription: {text}")
    
    print("STT Service initialized successfully")
    print(f"Provider: {stt.provider}")
    print(f"Model: {stt.model_name}")
