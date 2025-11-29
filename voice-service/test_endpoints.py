#!/usr/bin/env python3
"""
Test script for Voice Service endpoints
Tests STT (Faster Whisper) and TTS (Chatterbox) via RunPod
"""

import asyncio
import base64
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
STT_ENDPOINT = os.getenv("RUNPOD_STT_ENDPOINT", "rxfzl47istu4i2")
TTS_ENDPOINT = os.getenv("RUNPOD_TTS_ENDPOINT", "8bj9tg60e7nw6y")

# Test text
TEST_TEXT = "Hello, this is a test of the text to speech system."


async def test_tts():
    """Test TTS endpoint (Chatterbox)"""
    print("\n🎤 Testing TTS (Chatterbox)...")
    
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY not set")
        return None
    
    url = f"https://api.runpod.ai/v2/{TTS_ENDPOINT}/runsync"
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {
            "text": TEST_TEXT,
            "exaggeration": 0.5,
            "temperature": 0.8,
            "cfg_weight": 0.5
        }
    }
    
    print(f"   Endpoint: {TTS_ENDPOINT}")
    print(f"   Text: {TEST_TEXT}")
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error: {response.text}")
                return None
            
            result = response.json()
            status = result.get("status")
            print(f"   Job Status: {status}")
            
            # Poll if async
            if status in ["IN_QUEUE", "IN_PROGRESS"]:
                job_id = result.get("id")
                status_url = f"https://api.runpod.ai/v2/{TTS_ENDPOINT}/status/{job_id}"
                
                for i in range(60):
                    await asyncio.sleep(2)
                    status_resp = await client.get(status_url, headers=headers)
                    result = status_resp.json()
                    status = result.get("status")
                    print(f"   Polling... {status}")
                    
                    if status == "COMPLETED":
                        break
                    elif status == "FAILED":
                        print(f"❌ Job failed: {result}")
                        return None
            
            # Extract audio
            output = result.get("output", {})
            if isinstance(output, dict):
                audio_b64 = output.get("audio_base64", output.get("audio", ""))
            else:
                audio_b64 = str(output) if output else ""
            
            if audio_b64:
                audio_data = base64.b64decode(audio_b64)
                output_file = Path("test_output.wav")
                output_file.write_bytes(audio_data)
                print(f"✅ TTS Success! Audio saved to {output_file} ({len(audio_data)} bytes)")
                return audio_data
            else:
                print(f"⚠️ No audio in response: {result}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            return None


async def test_stt(audio_data: bytes = None):
    """Test STT endpoint (Faster Whisper)"""
    print("\n🎧 Testing STT (Faster Whisper)...")
    
    if not RUNPOD_API_KEY:
        print("❌ RUNPOD_API_KEY not set")
        return
    
    # Use provided audio or create simple test audio
    if audio_data is None:
        # Try to read test file if exists
        test_file = Path("test_output.wav")
        if test_file.exists():
            audio_data = test_file.read_bytes()
            print(f"   Using: {test_file}")
        else:
            print("⚠️ No audio file for STT test (run TTS first)")
            return
    
    url = f"https://api.runpod.ai/v2/{STT_ENDPOINT}/runsync"
    
    headers = {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json"
    }
    
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    payload = {
        "input": {
            "audio_base64": audio_b64,
            "model": "turbo",
            "transcription": "plain_text"
        }
    }
    
    print(f"   Endpoint: {STT_ENDPOINT}")
    print(f"   Audio size: {len(audio_data)} bytes")
    
    async with httpx.AsyncClient(timeout=120) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            print(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error: {response.text}")
                return
            
            result = response.json()
            status = result.get("status")
            print(f"   Job Status: {status}")
            
            # Poll if async
            if status in ["IN_QUEUE", "IN_PROGRESS"]:
                job_id = result.get("id")
                status_url = f"https://api.runpod.ai/v2/{STT_ENDPOINT}/status/{job_id}"
                
                for i in range(60):
                    await asyncio.sleep(2)
                    status_resp = await client.get(status_url, headers=headers)
                    result = status_resp.json()
                    status = result.get("status")
                    print(f"   Polling... {status}")
                    
                    if status == "COMPLETED":
                        break
                    elif status == "FAILED":
                        print(f"❌ Job failed: {result}")
                        return
            
            # Extract transcription
            output = result.get("output", {})
            if isinstance(output, dict):
                text = output.get("text", output.get("transcription", ""))
            else:
                text = str(output) if output else ""
            
            print(f"✅ STT Success!")
            print(f"   Transcription: \"{text}\"")
            
        except Exception as e:
            print(f"❌ Exception: {e}")


async def test_voice_service_api():
    """Test the local Voice Service API"""
    print("\n🌐 Testing Voice Service API...")
    
    base_url = os.getenv("VOICE_SERVICE_URL", "http://localhost:8765")
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Health check
            resp = await client.get(f"{base_url}/health")
            if resp.status_code == 200:
                print(f"✅ Server healthy: {resp.json()}")
            else:
                print(f"⚠️ Server returned: {resp.status_code}")
        except httpx.ConnectError:
            print("⚠️ Voice Service not running (start with: python server.py)")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    print("=" * 50)
    print("Voice Service - Endpoint Tests")
    print("=" * 50)
    
    if not RUNPOD_API_KEY:
        print("\n⚠️ RUNPOD_API_KEY not set!")
        print("   Set it in .env or environment variable")
        print("   Example: export RUNPOD_API_KEY=your-key")
        sys.exit(1)
    
    print(f"\n📋 Configuration:")
    print(f"   STT Endpoint: {STT_ENDPOINT}")
    print(f"   TTS Endpoint: {TTS_ENDPOINT}")
    
    # Test Voice Service API (if running)
    await test_voice_service_api()
    
    # Test TTS
    audio_data = await test_tts()
    
    # Test STT with TTS output
    if audio_data:
        await test_stt(audio_data)
    
    print("\n" + "=" * 50)
    print("Tests complete!")


if __name__ == "__main__":
    asyncio.run(main())
