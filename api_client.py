"""
Claude API Client
Handles communication with Claude API for voice-enabled conversations
"""

import os
import yaml
from pathlib import Path
from typing import Optional, AsyncIterator, List, Dict
import asyncio

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


class ClaudeAPIClient:
    """Client for interacting with Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config['apis']['anthropic_key'] or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")
        
        self.model = config['claude']['model']
        self.max_tokens = config['claude']['max_tokens']
        self.temperature = config['claude']['temperature']
        self.stream = config['claude']['stream']
        
        self.client = None
        self._initialize_client()
        
        # Conversation history
        self.messages: List[Dict] = []
    
    def _initialize_client(self):
        """Initialize Anthropic client"""
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=self.api_key)
            print("Claude API client initialized")
        except ImportError:
            print("Anthropic SDK not installed. Install with: pip install anthropic")
            raise
    
    def send_message(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a message to Claude and get response
        
        Args:
            user_message: User's message text
            system_prompt: Optional system prompt for context
            
        Returns:
            Claude's response text
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Create message
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": self.messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        response = self.client.messages.create(**kwargs)
        
        # Extract response text
        response_text = response.content[0].text
        
        # Add assistant message to history
        self.messages.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text
    
    async def send_message_streaming(
        self, 
        user_message: str, 
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Send a message to Claude with streaming response
        
        Args:
            user_message: User's message text
            system_prompt: Optional system prompt
            
        Yields:
            Response text chunks
        """
        # Add user message to history
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Create streaming message
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": self.messages
        }
        
        if system_prompt:
            kwargs["system"] = system_prompt
        
        full_response = ""
        
        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text
        
        # Add complete response to history
        self.messages.append({
            "role": "assistant",
            "content": full_response
        })
    
    def clear_history(self):
        """Clear conversation history"""
        self.messages = []
        print("Conversation history cleared")
    
    def get_history(self) -> List[Dict]:
        """Get conversation history"""
        return self.messages.copy()
    
    def set_system_context(self, context: str):
        """Set system context for the conversation"""
        self.system_prompt = context
    
    def export_conversation(self, file_path: str):
        """Export conversation history to JSON"""
        import json
        with open(file_path, 'w') as f:
            json.dump(self.messages, f, indent=2)
        print(f"Conversation exported to {file_path}")
    
    def import_conversation(self, file_path: str):
        """Import conversation history from JSON"""
        import json
        with open(file_path, 'r') as f:
            self.messages = json.load(f)
        print(f"Conversation imported from {file_path}")


class VoiceEnabledClaudeClient(ClaudeAPIClient):
    """Claude client with integrated voice capabilities"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        
        # Import voice manager
        import sys
        sys.path.append(str(Path(__file__).parent.parent / "core"))
        from voice_manager import VoiceManager
        
        self.voice = VoiceManager()
        print("Voice-enabled Claude client initialized")
    
    def voice_conversation(self, audio_data):
        """
        Have a voice conversation with Claude
        
        Args:
            audio_data: Audio input from microphone
            
        Returns:
            Audio response from Claude
        """
        # Transcribe user speech
        user_text = self.voice.listen(audio_data)
        print(f"You: {user_text}")
        
        # Get Claude's response
        response_text = self.send_message(user_text)
        print(f"Claude: {response_text}")
        
        # Synthesize response
        audio_response = self.voice.speak(response_text)
        
        return {
            "user_text": user_text,
            "response_text": response_text,
            "audio_response": audio_response
        }
    
    async def voice_conversation_streaming(self, audio_data):
        """
        Have a streaming voice conversation with Claude
        
        Args:
            audio_data: Audio input from microphone
            
        Yields:
            Audio chunks of Claude's response
        """
        # Transcribe user speech
        user_text = self.voice.listen(audio_data)
        print(f"You: {user_text}")
        
        response_text = ""
        
        # Stream Claude's text response
        async for text_chunk in self.send_message_streaming(user_text):
            response_text += text_chunk
            print(text_chunk, end='', flush=True)
        
        print()  # New line after streaming
        
        # Synthesize complete response
        async for audio_chunk in self.voice.speak_streaming(response_text):
            yield audio_chunk


# Example usage
if __name__ == "__main__":
    # Test basic Claude client
    # client = ClaudeAPIClient()
    # response = client.send_message("Hello! How are you today?")
    # print(f"Claude: {response}")
    
    # Test voice-enabled client
    # voice_client = VoiceEnabledClaudeClient()
    # print("Voice client ready. Send audio to start conversation.")
    
    print("Claude API clients initialized successfully")
