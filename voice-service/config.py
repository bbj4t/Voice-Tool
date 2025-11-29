#!/usr/bin/env python3
"""
Configuration management for Voice Service
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


CONFIG_FILE = Path.home() / ".voice-service" / "config.json"


@dataclass
class STTConfig:
    endpoint_id: str = "rxfzl47istu4i2"  # Faster Whisper 1.0.10
    api_key: str = ""


@dataclass
class TTSConfig:
    endpoint_id: str = "8bj9tg60e7nw6y"  # Chatterbox TTS v0.2.6
    api_key: str = ""


@dataclass
class LLMProvider:
    api_key: str = ""
    base_url: str = ""
    models: List[str] = field(default_factory=list)


@dataclass
class LLMConfig:
    active_provider: str = "openrouter"
    active_model: str = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
    providers: Dict[str, LLMProvider] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.providers:
            self.providers = {
                "openrouter": LLMProvider(
                    api_key=os.getenv("OPENROUTER_API_KEY", ""),
                    base_url="https://openrouter.ai/api/v1",
                    models=[
                        "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
                        "anthropic/claude-sonnet-4-20250514",
                        "openai/gpt-4o",
                        "google/gemini-pro",
                        "meta-llama/llama-3-70b-instruct"
                    ]
                ),
                "ollama": LLMProvider(
                    api_key="",
                    base_url="http://localhost:11434",
                    models=["llama3", "mistral", "codellama", "deepseek-coder"]
                ),
                "openai": LLMProvider(
                    api_key=os.getenv("OPENAI_API_KEY", ""),
                    base_url="https://api.openai.com/v1",
                    models=["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
                ),
                "anthropic": LLMProvider(
                    api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                    base_url="https://api.anthropic.com/v1",
                    models=["claude-sonnet-4-20250514", "claude-3-opus-20240229", "claude-3-haiku-20240307"]
                ),
                "groq": LLMProvider(
                    api_key=os.getenv("GROQ_API_KEY", ""),
                    base_url="https://api.groq.com/openai/v1",
                    models=["llama-3.1-70b-versatile", "mixtral-8x7b-32768"]
                ),
                "local": LLMProvider(
                    api_key="",
                    base_url="http://localhost:8080",
                    models=["local-model"]
                )
            }


@dataclass
class Config:
    stt: STTConfig = field(default_factory=STTConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)


def load_config() -> Config:
    """Load configuration from file and environment"""
    config = Config()
    
    # Load from file if exists
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            
            # STT
            if "stt" in data:
                config.stt.endpoint_id = data["stt"].get("endpoint_id", "")
                config.stt.api_key = data["stt"].get("api_key", "")
            
            # TTS
            if "tts" in data:
                config.tts.endpoint_id = data["tts"].get("endpoint_id", "")
                config.tts.api_key = data["tts"].get("api_key", "")
            
            # LLM
            if "llm" in data:
                config.llm.active_provider = data["llm"].get("active_provider", "openrouter")
                config.llm.active_model = data["llm"].get("active_model", "")
                
                if "providers" in data["llm"]:
                    for name, pdata in data["llm"]["providers"].items():
                        if name in config.llm.providers:
                            config.llm.providers[name].api_key = pdata.get("api_key", "")
                            if pdata.get("base_url"):
                                config.llm.providers[name].base_url = pdata["base_url"]
                            if pdata.get("models"):
                                config.llm.providers[name].models = pdata["models"]
                        else:
                            config.llm.providers[name] = LLMProvider(
                                api_key=pdata.get("api_key", ""),
                                base_url=pdata.get("base_url", ""),
                                models=pdata.get("models", [])
                            )
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Override with environment variables
    if os.getenv("RUNPOD_STT_ENDPOINT"):
        config.stt.endpoint_id = os.getenv("RUNPOD_STT_ENDPOINT")
    if os.getenv("RUNPOD_STT_API_KEY"):
        config.stt.api_key = os.getenv("RUNPOD_STT_API_KEY")
    if os.getenv("RUNPOD_API_KEY"):  # Shared key
        if not config.stt.api_key:
            config.stt.api_key = os.getenv("RUNPOD_API_KEY")
        if not config.tts.api_key:
            config.tts.api_key = os.getenv("RUNPOD_API_KEY")
    
    if os.getenv("RUNPOD_TTS_ENDPOINT"):
        config.tts.endpoint_id = os.getenv("RUNPOD_TTS_ENDPOINT")
    if os.getenv("RUNPOD_TTS_API_KEY"):
        config.tts.api_key = os.getenv("RUNPOD_TTS_API_KEY")
    
    return config


def save_config(config: Config):
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "stt": {
            "endpoint_id": config.stt.endpoint_id,
            "api_key": config.stt.api_key
        },
        "tts": {
            "endpoint_id": config.tts.endpoint_id,
            "api_key": config.tts.api_key
        },
        "llm": {
            "active_provider": config.llm.active_provider,
            "active_model": config.llm.active_model,
            "providers": {
                name: {
                    "api_key": p.api_key,
                    "base_url": p.base_url,
                    "models": p.models
                }
                for name, p in config.llm.providers.items()
            }
        }
    }
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
