#!/usr/bin/env python3
"""
Voice Service - Core API Server
Handles STT (RunPod), TTS (RunPod), and LLM routing
"""

import asyncio
import base64
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

# Load .env file before any other imports that use os.getenv
from dotenv import load_dotenv
load_dotenv()

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import Config, load_config, save_config
from providers import LLMRouter


# Global state
config: Config = None
llm_router: LLMRouter = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize on startup"""
    global config, llm_router
    config = load_config()
    llm_router = LLMRouter(config)
    print("🎤 Voice Service started")
    print(f"   STT: RunPod ({config.stt.endpoint_id})")
    print(f"   TTS: RunPod ({config.tts.endpoint_id})")
    print(f"   LLM: {config.llm.active_provider}")
    yield
    print("Voice Service stopped")


app = FastAPI(
    title="Voice Service",
    description="Private voice assistant API with configurable providers",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Models ============

class TranscribeRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = None  # None = auto-detect
    model: str = "turbo"  # base, turbo, large-v3
    transcription_format: str = "plain_text"  # plain_text, formatted_text, srt, vtt
    word_timestamps: bool = False

class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "default"
    # Chatterbox TTS parameters
    exaggeration: float = 0.5  # Neutral = 0.5, extreme values can be unstable
    temperature: float = 0.8
    cfg_weight: float = 0.5  # CFG/Pace
    audio_prompt_base64: Optional[str] = None  # Optional voice cloning prompt

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None
    provider: Optional[str] = None
    stream: bool = False

class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = []

class ConfigUpdate(BaseModel):
    stt_endpoint_id: Optional[str] = None
    stt_api_key: Optional[str] = None
    tts_endpoint_id: Optional[str] = None
    tts_api_key: Optional[str] = None
    active_llm_provider: Optional[str] = None
    active_llm_model: Optional[str] = None


# ============ STT (RunPod Faster Whisper) ============

async def transcribe_audio(
    audio_data: bytes,
    language: Optional[str] = None,
    model: str = "turbo",
    transcription_format: str = "plain_text",
    word_timestamps: bool = False
) -> str:
    """Send audio to RunPod Faster Whisper endpoint
    
    Faster Whisper parameters:
    - audio_base64: Base64 encoded audio
    - language: Language code (e.g., "en", "es") or None for auto-detect
    - model: Whisper model size (base, turbo, large-v3)
    - transcription_format: Output format (plain_text, formatted_text, srt, vtt)
    - word_timestamps: Whether to include word-level timestamps
    """
    if not config.stt.endpoint_id or not config.stt.api_key:
        raise HTTPException(status_code=400, detail="STT not configured")
    
    # RunPod serverless endpoint
    url = f"https://api.runpod.ai/v2/{config.stt.endpoint_id}/runsync"
    
    headers = {
        "Authorization": f"Bearer {config.stt.api_key}",
        "Content-Type": "application/json"
    }
    
    # Encode audio as base64
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    
    # Build Faster Whisper input payload
    input_params = {
        "audio_base64": audio_b64,
        "model": model,
        "transcription": transcription_format,
        "word_timestamps": word_timestamps
    }
    
    # Only include language if specified (None = auto-detect)
    if language:
        input_params["language"] = language
    
    payload = {"input": input_params}
    
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"STT error: {response.text}")
        
        result = response.json()
        
        # Handle RunPod async response
        if result.get("status") == "IN_QUEUE" or result.get("status") == "IN_PROGRESS":
            # Poll for result
            job_id = result.get("id")
            status_url = f"https://api.runpod.ai/v2/{config.stt.endpoint_id}/status/{job_id}"
            
            for _ in range(60):  # Max 60 seconds
                await asyncio.sleep(1)
                status_resp = await client.get(status_url, headers=headers)
                status_data = status_resp.json()
                
                if status_data.get("status") == "COMPLETED":
                    result = status_data
                    break
                elif status_data.get("status") == "FAILED":
                    raise HTTPException(status_code=500, detail="STT job failed")
        
        # Extract transcription
        output = result.get("output", {})
        if isinstance(output, dict):
            return output.get("text", output.get("transcription", ""))
        return str(output)


# ============ TTS (RunPod Chatterbox) ============

async def synthesize_speech(
    text: str,
    exaggeration: float = 0.5,
    temperature: float = 0.8,
    cfg_weight: float = 0.5,
    audio_prompt_base64: Optional[str] = None
) -> bytes:
    """Send text to RunPod Chatterbox TTS endpoint
    
    Chatterbox TTS parameters:
    - text: Text to synthesize
    - exaggeration: Emotion/expression level (0.25-2.0, neutral=0.5)
    - temperature: Sampling temperature (0.05-5.0, default=0.8)
    - cfg_weight: CFG/Pace weight (0.0-1.0, default=0.5)
    - audio_prompt_base64: Optional reference audio for voice cloning (base64 WAV)
    """
    if not config.tts.endpoint_id or not config.tts.api_key:
        raise HTTPException(status_code=400, detail="TTS not configured")
    
    url = f"https://api.runpod.ai/v2/{config.tts.endpoint_id}/runsync"
    
    headers = {
        "Authorization": f"Bearer {config.tts.api_key}",
        "Content-Type": "application/json"
    }
    
    # Build Chatterbox input payload
    input_params = {
        "text": text,
        "exaggeration": exaggeration,
        "temperature": temperature,
        "cfg_weight": cfg_weight,
    }
    
    # Add voice cloning reference if provided
    if audio_prompt_base64:
        input_params["audio_prompt_base64"] = audio_prompt_base64
    
    payload = {"input": input_params}
    
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"TTS error: {response.text}")
        
        result = response.json()
        
        # Handle async response
        if result.get("status") in ["IN_QUEUE", "IN_PROGRESS"]:
            job_id = result.get("id")
            status_url = f"https://api.runpod.ai/v2/{config.tts.endpoint_id}/status/{job_id}"
            
            for _ in range(60):
                await asyncio.sleep(1)
                status_resp = await client.get(status_url, headers=headers)
                status_data = status_resp.json()
                
                if status_data.get("status") == "COMPLETED":
                    result = status_data
                    break
                elif status_data.get("status") == "FAILED":
                    raise HTTPException(status_code=500, detail="TTS job failed")
        
        # Extract audio (base64 encoded)
        output = result.get("output", {})
        if isinstance(output, dict):
            audio_b64 = output.get("audio_base64", output.get("audio", ""))
        else:
            audio_b64 = str(output)
        
        return base64.b64decode(audio_b64)


# ============ API Routes ============

@app.get("/")
async def root():
    return {"status": "ok", "service": "Voice Service", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "stt_configured": bool(config.stt.endpoint_id),
        "tts_configured": bool(config.tts.endpoint_id),
        "llm_provider": config.llm.active_provider,
        "llm_model": config.llm.active_model
    }


# ---- STT ----

@app.post("/stt/transcribe")
async def api_transcribe(request: TranscribeRequest):
    """Transcribe audio (base64) to text"""
    audio_data = base64.b64decode(request.audio_base64)
    text = await transcribe_audio(
        audio_data,
        language=request.language,
        model=request.model,
        transcription_format=request.transcription_format,
        word_timestamps=request.word_timestamps
    )
    return {"text": text}


@app.post("/stt/transcribe-file")
async def api_transcribe_file(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    model: str = "turbo"
):
    """Transcribe uploaded audio file"""
    audio_data = await file.read()
    text = await transcribe_audio(audio_data, language=language, model=model)
    return {"text": text}


# ---- TTS ----

@app.post("/tts/synthesize")
async def api_synthesize(request: SynthesizeRequest):
    """Synthesize text to speech, return base64 audio"""
    audio_data = await synthesize_speech(
        request.text,
        exaggeration=request.exaggeration,
        temperature=request.temperature,
        cfg_weight=request.cfg_weight,
        audio_prompt_base64=request.audio_prompt_base64
    )
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    return {"audio_base64": audio_b64}


@app.post("/tts/synthesize-file")
async def api_synthesize_file(request: SynthesizeRequest):
    """Synthesize text and return audio file"""
    audio_data = await synthesize_speech(
        request.text,
        exaggeration=request.exaggeration,
        temperature=request.temperature,
        cfg_weight=request.cfg_weight,
        audio_prompt_base64=request.audio_prompt_base64
    )
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_data)
        return FileResponse(f.name, media_type="audio/wav", filename="speech.wav")


# ---- LLM ----

@app.post("/llm/chat")
async def api_chat(request: ChatRequest):
    """Chat with LLM"""
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    
    provider = request.provider or config.llm.active_provider
    model = request.model or config.llm.active_model
    
    response = await llm_router.chat(messages, provider=provider, model=model)
    return {"response": response, "provider": provider, "model": model}


@app.get("/llm/providers")
async def api_get_providers():
    """Get available LLM providers and models"""
    return {
        "active_provider": config.llm.active_provider,
        "active_model": config.llm.active_model,
        "providers": {
            name: {
                "configured": bool(p.api_key) if name != "ollama" else True,
                "base_url": p.base_url,
                "models": p.models
            }
            for name, p in config.llm.providers.items()
        }
    }


@app.post("/llm/providers/{provider_name}")
async def api_add_provider(provider_name: str, provider: ProviderConfig):
    """Add or update an LLM provider"""
    config.llm.providers[provider_name] = type('Provider', (), {
        'api_key': provider.api_key,
        'base_url': provider.base_url,
        'models': provider.models
    })()
    save_config(config)
    return {"status": "ok", "provider": provider_name}


@app.post("/llm/set-active")
async def api_set_active_llm(provider: str, model: str):
    """Set active LLM provider and model"""
    config.llm.active_provider = provider
    config.llm.active_model = model
    save_config(config)
    return {"status": "ok", "provider": provider, "model": model}


# ---- Voice Chat (Combined) ----

@app.post("/voice/chat")
async def api_voice_chat(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    exaggeration: float = 0.5,
    temperature: float = 0.8,
    cfg_weight: float = 0.5
):
    """Complete voice chat: STT -> LLM -> TTS"""
    # 1. Transcribe
    audio_data = await file.read()
    user_text = await transcribe_audio(audio_data, language=language)
    
    # 2. Chat with LLM
    messages = [{"role": "user", "content": user_text}]
    response_text = await llm_router.chat(messages)
    
    # 3. Synthesize response
    response_audio = await synthesize_speech(
        response_text,
        exaggeration=exaggeration,
        temperature=temperature,
        cfg_weight=cfg_weight
    )
    audio_b64 = base64.b64encode(response_audio).decode('utf-8')
    
    return {
        "user_text": user_text,
        "response_text": response_text,
        "response_audio_base64": audio_b64
    }


# ---- Config ----

@app.get("/config")
async def api_get_config():
    """Get current configuration (without sensitive keys)"""
    return {
        "stt": {
            "endpoint_id": config.stt.endpoint_id,
            "configured": bool(config.stt.api_key)
        },
        "tts": {
            "endpoint_id": config.tts.endpoint_id,
            "configured": bool(config.tts.api_key)
        },
        "llm": {
            "active_provider": config.llm.active_provider,
            "active_model": config.llm.active_model,
            "providers": list(config.llm.providers.keys())
        }
    }


@app.post("/config")
async def api_update_config(update: ConfigUpdate):
    """Update configuration"""
    if update.stt_endpoint_id:
        config.stt.endpoint_id = update.stt_endpoint_id
    if update.stt_api_key:
        config.stt.api_key = update.stt_api_key
    if update.tts_endpoint_id:
        config.tts.endpoint_id = update.tts_endpoint_id
    if update.tts_api_key:
        config.tts.api_key = update.tts_api_key
    if update.active_llm_provider:
        config.llm.active_provider = update.active_llm_provider
    if update.active_llm_model:
        config.llm.active_model = update.active_llm_model
    
    save_config(config)
    return {"status": "ok"}


# ============ WebSocket for Streaming ============

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_json(self, websocket: WebSocket, data: dict):
        await websocket.send_json(data)


manager = ConnectionManager()


@app.websocket("/ws/voice")
async def websocket_voice(websocket: WebSocket):
    """WebSocket for real-time voice chat"""
    await manager.connect(websocket)
    conversation_history = []
    
    # TTS settings (can be updated via messages)
    tts_settings = {
        "exaggeration": 0.5,
        "temperature": 0.8,
        "cfg_weight": 0.5,
        "audio_prompt_base64": None
    }
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "audio":
                # Transcribe
                audio_b64 = data.get("audio_base64", "")
                audio_data = base64.b64decode(audio_b64)
                
                await manager.send_json(websocket, {"type": "status", "message": "Transcribing..."})
                user_text = await transcribe_audio(
                    audio_data,
                    language=data.get("language"),
                    model=data.get("model", "turbo")
                )
                
                await manager.send_json(websocket, {"type": "transcription", "text": user_text})
                
                # Add to history and chat
                conversation_history.append({"role": "user", "content": user_text})
                
                await manager.send_json(websocket, {"type": "status", "message": "Thinking..."})
                response_text = await llm_router.chat(conversation_history)
                
                conversation_history.append({"role": "assistant", "content": response_text})
                
                await manager.send_json(websocket, {"type": "response", "text": response_text})
                
                # Synthesize with current TTS settings
                await manager.send_json(websocket, {"type": "status", "message": "Synthesizing..."})
                response_audio = await synthesize_speech(
                    response_text,
                    exaggeration=tts_settings["exaggeration"],
                    temperature=tts_settings["temperature"],
                    cfg_weight=tts_settings["cfg_weight"],
                    audio_prompt_base64=tts_settings["audio_prompt_base64"]
                )
                audio_b64 = base64.b64encode(response_audio).decode('utf-8')
                
                await manager.send_json(websocket, {
                    "type": "audio",
                    "audio_base64": audio_b64
                })
            
            elif data.get("type") == "clear":
                conversation_history = []
                await manager.send_json(websocket, {"type": "status", "message": "Conversation cleared"})
            
            elif data.get("type") == "settings":
                # Update TTS settings
                if "exaggeration" in data:
                    tts_settings["exaggeration"] = data["exaggeration"]
                if "temperature" in data:
                    tts_settings["temperature"] = data["temperature"]
                if "cfg_weight" in data:
                    tts_settings["cfg_weight"] = data["cfg_weight"]
                if "audio_prompt_base64" in data:
                    tts_settings["audio_prompt_base64"] = data["audio_prompt_base64"]
                await manager.send_json(websocket, {"type": "status", "message": "Settings updated"})
            
            elif data.get("type") == "text":
                # Text-only chat
                user_text = data.get("text", "")
                conversation_history.append({"role": "user", "content": user_text})
                
                response_text = await llm_router.chat(conversation_history)
                conversation_history.append({"role": "assistant", "content": response_text})
                
                await manager.send_json(websocket, {"type": "response", "text": response_text})
                
                # Optionally synthesize if requested
                if data.get("synthesize", False):
                    response_audio = await synthesize_speech(
                        response_text,
                        exaggeration=tts_settings["exaggeration"],
                        temperature=tts_settings["temperature"],
                        cfg_weight=tts_settings["cfg_weight"],
                        audio_prompt_base64=tts_settings["audio_prompt_base64"]
                    )
                    audio_b64 = base64.b64encode(response_audio).decode('utf-8')
                    await manager.send_json(websocket, {"type": "audio", "audio_base64": audio_b64})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============ Main ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
