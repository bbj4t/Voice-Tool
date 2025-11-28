"""
Bridge Server
WebSocket server for real-time voice interaction with Claude
"""

import asyncio
import json
import base64
import numpy as np
from pathlib import Path
import yaml
import sys

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent))

from voice_manager import VoiceManager
from api_client import VoiceEnabledClaudeClient

# Load configuration
config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)


class VoiceBridgeServer:
    """WebSocket server bridging voice input/output with Claude"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or config['server']['host']
        self.port = port or config['server']['websocket_port']
        self.claude_client = VoiceEnabledClaudeClient()
        self.active_connections = set()
        
        print(f"Voice Bridge Server initialized on {self.host}:{self.port}")
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        client_id = id(websocket)
        self.active_connections.add(websocket)
        print(f"Client connected: {client_id}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except Exception as e:
            print(f"Error with client {client_id}: {e}")
        finally:
            self.active_connections.remove(websocket)
            print(f"Client disconnected: {client_id}")
    
    async def process_message(self, websocket, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'audio':
                await self.handle_audio(websocket, data)
            elif msg_type == 'text':
                await self.handle_text(websocket, data)
            elif msg_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {msg_type}'
                }))
        
        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    async def handle_audio(self, websocket, data):
        """Handle incoming audio data"""
        try:
            # Decode base64 audio
            audio_b64 = data.get('audio')
            audio_bytes = base64.b64decode(audio_b64)
            
            # Convert to numpy array (assuming 16-bit PCM)
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            
            # Send transcription status
            await websocket.send(json.dumps({
                'type': 'status',
                'message': 'Transcribing...'
            }))
            
            # Transcribe audio
            user_text = self.claude_client.voice.listen(audio_data)
            
            # Send transcription
            await websocket.send(json.dumps({
                'type': 'transcription',
                'text': user_text
            }))
            
            # Send processing status
            await websocket.send(json.dumps({
                'type': 'status',
                'message': 'Thinking...'
            }))
            
            # Get Claude's response (streaming)
            response_text = ""
            async for text_chunk in self.claude_client.send_message_streaming(user_text):
                response_text += text_chunk
                await websocket.send(json.dumps({
                    'type': 'response_chunk',
                    'text': text_chunk
                }))
            
            # Send synthesis status
            await websocket.send(json.dumps({
                'type': 'status',
                'message': 'Generating speech...'
            }))
            
            # Synthesize response
            audio_response = self.claude_client.voice.speak(response_text)
            audio_b64 = base64.b64encode(audio_response).decode('utf-8')
            
            # Send audio response
            await websocket.send(json.dumps({
                'type': 'audio_response',
                'audio': audio_b64,
                'text': response_text
            }))
            
            # Send completion
            await websocket.send(json.dumps({
                'type': 'complete'
            }))
        
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Audio processing error: {str(e)}'
            }))
    
    async def handle_text(self, websocket, data):
        """Handle incoming text message"""
        try:
            user_text = data.get('text')
            
            # Send processing status
            await websocket.send(json.dumps({
                'type': 'status',
                'message': 'Thinking...'
            }))
            
            # Get Claude's response (streaming)
            response_text = ""
            async for text_chunk in self.claude_client.send_message_streaming(user_text):
                response_text += text_chunk
                await websocket.send(json.dumps({
                    'type': 'response_chunk',
                    'text': text_chunk
                }))
            
            # Optionally synthesize if requested
            if data.get('synthesize', False):
                await websocket.send(json.dumps({
                    'type': 'status',
                    'message': 'Generating speech...'
                }))
                
                audio_response = self.claude_client.voice.speak(response_text)
                audio_b64 = base64.b64encode(audio_response).decode('utf-8')
                
                await websocket.send(json.dumps({
                    'type': 'audio_response',
                    'audio': audio_b64,
                    'text': response_text
                }))
            
            # Send completion
            await websocket.send(json.dumps({
                'type': 'complete'
            }))
        
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': f'Text processing error: {str(e)}'
            }))
    
    async def start(self):
        """Start the WebSocket server"""
        try:
            import websockets
        except ImportError:
            print("websockets not installed. Install with: pip install websockets")
            return
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"Voice Bridge Server running on ws://{self.host}:{self.port}")
            print("Ready for voice connections...")
            await asyncio.Future()  # Run forever


# HTTP API Server (for REST endpoints)
class HTTPAPIServer:
    """HTTP API for voice services"""
    
    def __init__(self, host: str = None, port: int = None):
        self.host = host or config['server']['host']
        self.port = port or config['server']['port']
        self.claude_client = VoiceEnabledClaudeClient()
    
    async def start(self):
        """Start the HTTP API server"""
        try:
            from aiohttp import web
        except ImportError:
            print("aiohttp not installed. Install with: pip install aiohttp")
            return
        
        app = web.Application()
        app.router.add_get('/health', self.health_check)
        app.router.add_post('/transcribe', self.transcribe)
        app.router.add_post('/synthesize', self.synthesize)
        app.router.add_post('/conversation', self.conversation)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        print(f"HTTP API Server running on http://{self.host}:{self.port}")
        print("Endpoints:")
        print("  GET  /health - Health check")
        print("  POST /transcribe - Transcribe audio")
        print("  POST /synthesize - Synthesize text")
        print("  POST /conversation - Full voice conversation")
    
    async def health_check(self, request):
        """Health check endpoint"""
        from aiohttp import web
        return web.json_response({
            'status': 'healthy',
            'services': {
                'stt': self.claude_client.voice.stt.provider,
                'tts': self.claude_client.voice.tts.provider,
                'claude': self.claude_client.model
            }
        })
    
    async def transcribe(self, request):
        """Transcribe audio endpoint"""
        from aiohttp import web
        
        data = await request.json()
        audio_b64 = data.get('audio')
        
        if not audio_b64:
            return web.json_response({'error': 'No audio provided'}, status=400)
        
        audio_bytes = base64.b64decode(audio_b64)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        text = self.claude_client.voice.listen(audio_data)
        
        return web.json_response({'text': text})
    
    async def synthesize(self, request):
        """Synthesize text endpoint"""
        from aiohttp import web
        
        data = await request.json()
        text = data.get('text')
        
        if not text:
            return web.json_response({'error': 'No text provided'}, status=400)
        
        audio = self.claude_client.voice.speak(text)
        audio_b64 = base64.b64encode(audio).decode('utf-8')
        
        return web.json_response({'audio': audio_b64})
    
    async def conversation(self, request):
        """Full conversation endpoint"""
        from aiohttp import web
        
        data = await request.json()
        audio_b64 = data.get('audio')
        
        if not audio_b64:
            return web.json_response({'error': 'No audio provided'}, status=400)
        
        audio_bytes = base64.b64decode(audio_b64)
        audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        result = self.claude_client.voice_conversation(audio_data)
        result['audio_response'] = base64.b64encode(result['audio_response']).decode('utf-8')
        
        return web.json_response(result)


async def main():
    """Run both WebSocket and HTTP servers"""
    ws_server = VoiceBridgeServer()
    http_server = HTTPAPIServer()
    
    # Start both servers
    await asyncio.gather(
        ws_server.start(),
        http_server.start()
    )


if __name__ == "__main__":
    print("Starting Voice Bridge Servers...")
    asyncio.run(main())
