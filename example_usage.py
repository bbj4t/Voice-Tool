"""
Example Scripts for Voice Development Wrapper
Demonstrates various use cases and features
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent.parent / "claude-bridge"))

import numpy as np
import asyncio


def example_1_simple_transcription():
    """Example 1: Simple audio transcription"""
    print("=" * 60)
    print("Example 1: Simple Audio Transcription")
    print("=" * 60)
    
    from voice_manager import VoiceManager
    
    vm = VoiceManager()
    
    # For this example, you would record or load actual audio
    # Here we'll show the API usage
    
    print("\n1. Load or record audio")
    print("   audio_file = 'your_recording.wav'")
    print("   text = vm.transcribe_file(audio_file)")
    print("\n2. Result will be the transcribed text")
    
    print("\n✓ Example complete - see USAGE_GUIDE.md for details")


def example_2_text_to_speech():
    """Example 2: Text-to-speech synthesis"""
    print("\n" + "=" * 60)
    print("Example 2: Text-to-Speech Synthesis")
    print("=" * 60)
    
    from voice_manager import VoiceManager
    
    vm = VoiceManager()
    
    text = "This is an example of text to speech synthesis."
    
    print(f"\n1. Text to synthesize: '{text}'")
    print("\n2. Synthesizing...")
    
    # Synthesize would create audio file
    # vm.synthesize_to_file(text, "example_output.mp3")
    
    print("\n3. Available voices:")
    voices = vm.tts.get_available_voices()
    for voice in voices:
        print(f"   • {voice}")
    
    print("\n✓ Example complete")


def example_3_claude_conversation():
    """Example 3: Text conversation with Claude"""
    print("\n" + "=" * 60)
    print("Example 3: Text Conversation with Claude")
    print("=" * 60)
    
    from api_client import ClaudeAPIClient
    
    print("\n1. Initialize Claude client")
    # client = ClaudeAPIClient()
    
    print("\n2. Send a message")
    # response = client.send_message("Explain Python decorators in simple terms")
    
    print("\n3. Get Claude's response")
    # print(f"Claude: {response}")
    
    print("\n4. Continue the conversation")
    # response2 = client.send_message("Can you give me a code example?")
    
    print("\n✓ Example complete - requires API key configuration")


async def example_4_streaming_response():
    """Example 4: Streaming Claude responses"""
    print("\n" + "=" * 60)
    print("Example 4: Streaming Claude Responses")
    print("=" * 60)
    
    from api_client import ClaudeAPIClient
    
    print("\n1. Initialize Claude client with streaming")
    # client = ClaudeAPIClient()
    
    print("\n2. Send message and stream response")
    # async for chunk in client.send_message_streaming("Write a short poem"):
    #     print(chunk, end='', flush=True)
    
    print("\n\n✓ Example complete - requires API key configuration")


def example_5_voice_conversation():
    """Example 5: Complete voice conversation"""
    print("\n" + "=" * 60)
    print("Example 5: Complete Voice Conversation")
    print("=" * 60)
    
    from api_client import VoiceEnabledClaudeClient
    
    print("\n1. Initialize voice-enabled Claude client")
    # client = VoiceEnabledClaudeClient()
    
    print("\n2. Record audio (your voice)")
    # import sounddevice as sd
    # duration = 5
    # sample_rate = 16000
    # audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    # sd.wait()
    
    print("\n3. Have conversation")
    # result = client.voice_conversation(audio.flatten())
    # print(f"You: {result['user_text']}")
    # print(f"Claude: {result['response_text']}")
    
    print("\n4. Play Claude's audio response")
    # (use audio playback library of choice)
    
    print("\n✓ Example complete - requires API keys and audio hardware")


def example_6_websocket_client():
    """Example 6: WebSocket client for real-time interaction"""
    print("\n" + "=" * 60)
    print("Example 6: WebSocket Client")
    print("=" * 60)
    
    print("""
import asyncio
import websockets
import json
import base64

async def voice_chat():
    uri = "ws://localhost:8766"
    
    async with websockets.connect(uri) as websocket:
        # Record audio
        audio_data = record_audio()  # Your recording function
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Send audio message
        await websocket.send(json.dumps({
            "type": "audio",
            "audio": audio_b64
        }))
        
        # Receive responses
        async for message in websocket:
            data = json.loads(message)
            
            if data['type'] == 'transcription':
                print(f"You: {data['text']}")
            
            elif data['type'] == 'response_chunk':
                print(data['text'], end='', flush=True)
            
            elif data['type'] == 'audio_response':
                print(f"\\nClaude: {data['text']}")
                # Play audio: base64.b64decode(data['audio'])
            
            elif data['type'] == 'complete':
                break

asyncio.run(voice_chat())
""")
    
    print("\n✓ Example complete - requires bridge server running")


def example_7_custom_config():
    """Example 7: Custom configuration"""
    print("\n" + "=" * 60)
    print("Example 7: Custom Configuration")
    print("=" * 60)
    
    print("\nCustomize voice settings programmatically:\n")
    
    print("""
from voice_manager import VoiceManager

vm = VoiceManager()

# Change TTS voice
vm.change_voice("shimmer")

# Change STT model
vm.change_stt_model("medium")  # More accurate but slower

# Check status
status = vm.get_status()
print(f"Current STT: {status['stt_provider']}")
print(f"Current TTS: {status['tts_provider']}")
print(f"Available voices: {status['available_voices']}")
""")
    
    print("\n✓ Example complete")


def example_8_batch_processing():
    """Example 8: Batch audio processing"""
    print("\n" + "=" * 60)
    print("Example 8: Batch Audio Processing")
    print("=" * 60)
    
    print("\nProcess multiple audio files:\n")
    
    print("""
from voice_manager import VoiceManager
from pathlib import Path

vm = VoiceManager()

audio_dir = Path("audio_files")
output_dir = Path("transcriptions")
output_dir.mkdir(exist_ok=True)

# Process all audio files
for audio_file in audio_dir.glob("*.wav"):
    print(f"Processing: {audio_file.name}")
    
    # Transcribe
    text = vm.transcribe_file(str(audio_file))
    
    # Save transcription
    output_file = output_dir / f"{audio_file.stem}.txt"
    output_file.write_text(text)
    
    print(f"Saved to: {output_file}")

print(f"Processed {len(list(audio_dir.glob('*.wav')))} files")
""")
    
    print("\n✓ Example complete")


def example_9_conversation_history():
    """Example 9: Managing conversation history"""
    print("\n" + "=" * 60)
    print("Example 9: Managing Conversation History")
    print("=" * 60)
    
    print("\nWork with conversation history:\n")
    
    print("""
from api_client import ClaudeAPIClient

client = ClaudeAPIClient()

# Have multiple exchanges
client.send_message("What is Python?")
client.send_message("How do I install it?")
client.send_message("What's a good first project?")

# Export conversation
client.export_conversation("python_help_session.json")

# Later, continue the conversation
client2 = ClaudeAPIClient()
client2.import_conversation("python_help_session.json")
response = client2.send_message("Can you review my code?")

# Clear history when done
client2.clear_history()
""")
    
    print("\n✓ Example complete")


def example_10_error_handling():
    """Example 10: Error handling and retries"""
    print("\n" + "=" * 60)
    print("Example 10: Error Handling")
    print("=" * 60)
    
    print("\nRobust error handling:\n")
    
    print("""
from voice_manager import VoiceManager
from api_client import ClaudeAPIClient
import time

def safe_transcribe(audio_data, max_retries=3):
    vm = VoiceManager()
    
    for attempt in range(max_retries):
        try:
            text = vm.listen(audio_data)
            return text
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    
def safe_claude_message(message, max_retries=3):
    client = ClaudeAPIClient()
    
    for attempt in range(max_retries):
        try:
            response = client.send_message(message)
            return response
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

# Usage
try:
    text = safe_transcribe(audio_data)
    response = safe_claude_message(text)
    print(f"Success: {response}")
except Exception as e:
    print(f"Failed after retries: {e}")
""")
    
    print("\n✓ Example complete")


def run_all_examples():
    """Run all examples"""
    examples = [
        example_1_simple_transcription,
        example_2_text_to_speech,
        example_3_claude_conversation,
        # example_4_streaming_response,  # Async
        example_5_voice_conversation,
        example_6_websocket_client,
        example_7_custom_config,
        example_8_batch_processing,
        example_9_conversation_history,
        example_10_error_handling,
    ]
    
    print("\n" + "=" * 60)
    print("Voice Development Wrapper - Example Scripts")
    print("=" * 60)
    
    for i, example in enumerate(examples, 1):
        example()
        if i < len(examples):
            input("\n\nPress Enter to continue to next example...")


if __name__ == "__main__":
    print("\nVoice Development Wrapper - Examples")
    print("\nThese examples demonstrate various features and use cases.")
    print("Note: Most examples require API key configuration and some")
    print("require audio hardware or running services.")
    print("\nFor detailed setup, see README.md and USAGE_GUIDE.md")
    
    choice = input("\nRun all examples? (y/n): ").lower()
    
    if choice == 'y':
        run_all_examples()
    else:
        print("\nExamples available:")
        print("  1. Simple Transcription")
        print("  2. Text-to-Speech")
        print("  3. Claude Conversation")
        print("  4. Streaming Response")
        print("  5. Voice Conversation")
        print("  6. WebSocket Client")
        print("  7. Custom Configuration")
        print("  8. Batch Processing")
        print("  9. Conversation History")
        print(" 10. Error Handling")
        
        num = input("\nEnter example number (1-10): ")
        examples = {
            '1': example_1_simple_transcription,
            '2': example_2_text_to_speech,
            '3': example_3_claude_conversation,
            '5': example_5_voice_conversation,
            '6': example_6_websocket_client,
            '7': example_7_custom_config,
            '8': example_8_batch_processing,
            '9': example_9_conversation_history,
            '10': example_10_error_handling,
        }
        
        if num in examples:
            examples[num]()
        else:
            print("Invalid selection")
