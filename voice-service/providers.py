#!/usr/bin/env python3
"""
LLM Provider Router - handles multiple LLM backends
"""

import httpx
from typing import List, Dict, Any, Optional

from config import Config


class LLMRouter:
    """Routes LLM requests to configured providers"""
    
    def __init__(self, config: Config):
        self.config = config
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """Send chat request to LLM provider"""
        provider = provider or self.config.llm.active_provider
        model = model or self.config.llm.active_model
        
        provider_config = self.config.llm.providers.get(provider)
        if not provider_config:
            raise ValueError(f"Unknown provider: {provider}")
        
        # Route to appropriate handler
        if provider == "ollama":
            return await self._chat_ollama(messages, model, provider_config)
        elif provider == "anthropic":
            return await self._chat_anthropic(messages, model, provider_config)
        else:
            # OpenAI-compatible API (OpenRouter, OpenAI, Groq, local)
            return await self._chat_openai_compatible(messages, model, provider_config, provider)
    
    async def _chat_openai_compatible(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider_config,
        provider_name: str
    ) -> str:
        """Chat with OpenAI-compatible API"""
        headers = {
            "Content-Type": "application/json"
        }
        
        if provider_config.api_key:
            headers["Authorization"] = f"Bearer {provider_config.api_key}"
        
        # OpenRouter specific headers
        if provider_name == "openrouter":
            headers["HTTP-Referer"] = "https://voice-service.local"
            headers["X-Title"] = "Voice Service"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{provider_config.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"LLM error ({provider_name}): {response.status_code} - {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider_config
    ) -> str:
        """Chat with local Ollama"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{provider_config.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["message"]["content"]
    
    async def _chat_anthropic(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider_config
    ) -> str:
        """Chat with Anthropic API (native format)"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": provider_config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages format
        system_message = ""
        chat_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)
        
        payload = {
            "model": model,
            "max_tokens": 4096,
            "messages": chat_messages
        }
        
        if system_message:
            payload["system"] = system_message
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{provider_config.base_url}/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic error: {response.status_code} - {response.text}")
            
            result = response.json()
            return result["content"][0]["text"]
    
    async def list_models(self, provider: str) -> List[str]:
        """List available models for a provider"""
        provider_config = self.config.llm.providers.get(provider)
        if not provider_config:
            return []
        
        # For Ollama, we can query available models
        if provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{provider_config.base_url}/api/tags")
                    if response.status_code == 200:
                        result = response.json()
                        return [m["name"] for m in result.get("models", [])]
            except:
                pass
        
        # Return configured models
        return provider_config.models
