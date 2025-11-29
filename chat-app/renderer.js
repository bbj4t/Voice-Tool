/**
 * Voice Chat - Renderer Process
 * Handles UI interactions and Voice Service communication
 */

class VoiceChat {
  constructor() {
    this.serverUrl = 'http://localhost:8765';
    this.ws = null;
    this.isConnected = false;
    this.isRecording = false;
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.conversationHistory = [];
    
    // TTS settings
    this.ttsSettings = {
      exaggeration: 0.5,
      temperature: 0.8,
      cfgWeight: 0.5
    };
    
    // Provider/model info
    this.providers = {};
    this.activeProvider = 'openrouter';
    this.activeModel = '';
    
    this.init();
  }
  
  async init() {
    this.bindElements();
    this.bindEvents();
    await this.loadSettings();
    this.connect();
  }
  
  bindElements() {
    // Sidebar
    this.providerSelect = document.getElementById('provider-select');
    this.modelSelect = document.getElementById('model-select');
    this.serverUrlInput = document.getElementById('server-url');
    this.connectBtn = document.getElementById('connect-btn');
    this.connectionStatus = document.getElementById('connection-status');
    this.clearChatBtn = document.getElementById('clear-chat');
    this.settingsBtn = document.getElementById('settings-btn');
    
    // TTS sliders
    this.exaggerationSlider = document.getElementById('tts-exaggeration');
    this.temperatureSlider = document.getElementById('tts-temperature');
    this.cfgSlider = document.getElementById('tts-cfg');
    this.exaggerationValue = document.getElementById('exaggeration-value');
    this.temperatureValue = document.getElementById('temperature-value');
    this.cfgValue = document.getElementById('cfg-value');
    
    // Chat
    this.chatMessages = document.getElementById('chat-messages');
    this.textInput = document.getElementById('text-input');
    this.sendBtn = document.getElementById('send-btn');
    this.micBtn = document.getElementById('mic-btn');
    
    // Modal
    this.settingsModal = document.getElementById('settings-modal');
    this.saveSettingsBtn = document.getElementById('save-settings');
    this.closeSettingsBtn = document.getElementById('close-settings');
  }
  
  bindEvents() {
    // Connection
    this.connectBtn.addEventListener('click', () => this.connect());
    this.serverUrlInput.addEventListener('change', (e) => {
      this.serverUrl = e.target.value;
    });
    
    // Provider/Model
    this.providerSelect.addEventListener('change', (e) => {
      this.selectProvider(e.target.value);
    });
    this.modelSelect.addEventListener('change', (e) => {
      this.selectModel(e.target.value);
    });
    
    // TTS sliders
    this.exaggerationSlider.addEventListener('input', (e) => {
      this.ttsSettings.exaggeration = parseFloat(e.target.value);
      this.exaggerationValue.textContent = e.target.value;
      this.sendTTSSettings();
    });
    this.temperatureSlider.addEventListener('input', (e) => {
      this.ttsSettings.temperature = parseFloat(e.target.value);
      this.temperatureValue.textContent = e.target.value;
      this.sendTTSSettings();
    });
    this.cfgSlider.addEventListener('input', (e) => {
      this.ttsSettings.cfgWeight = parseFloat(e.target.value);
      this.cfgValue.textContent = e.target.value;
      this.sendTTSSettings();
    });
    
    // Chat input
    this.textInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.sendTextMessage();
      }
    });
    this.textInput.addEventListener('input', () => {
      this.textInput.style.height = 'auto';
      this.textInput.style.height = Math.min(this.textInput.scrollHeight, 120) + 'px';
    });
    this.sendBtn.addEventListener('click', () => this.sendTextMessage());
    
    // Mic button - hold to record
    this.micBtn.addEventListener('mousedown', () => this.startRecording());
    this.micBtn.addEventListener('mouseup', () => this.stopRecording());
    this.micBtn.addEventListener('mouseleave', () => {
      if (this.isRecording) this.stopRecording();
    });
    // Touch support
    this.micBtn.addEventListener('touchstart', (e) => {
      e.preventDefault();
      this.startRecording();
    });
    this.micBtn.addEventListener('touchend', (e) => {
      e.preventDefault();
      this.stopRecording();
    });
    
    // Clear chat
    this.clearChatBtn.addEventListener('click', () => this.clearChat());
    
    // Settings modal
    this.settingsBtn.addEventListener('click', () => {
      this.settingsModal.classList.remove('hidden');
    });
    this.closeSettingsBtn.addEventListener('click', () => {
      this.settingsModal.classList.add('hidden');
    });
    this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
  }
  
  async loadSettings() {
    // Try to load from Electron store if available
    if (window.electronAPI) {
      try {
        const settings = await window.electronAPI.getSettings();
        if (settings.voiceServiceUrl) {
          this.serverUrl = settings.voiceServiceUrl;
          this.serverUrlInput.value = this.serverUrl;
        }
        if (settings.ttsExaggeration) {
          this.ttsSettings.exaggeration = settings.ttsExaggeration;
          this.exaggerationSlider.value = settings.ttsExaggeration;
          this.exaggerationValue.textContent = settings.ttsExaggeration;
        }
      } catch (e) {
        console.log('No saved settings');
      }
    }
  }
  
  async saveSettings() {
    // Save API keys via the voice service
    const keys = {
      openrouter: document.getElementById('openrouter-key').value,
      openai: document.getElementById('openai-key').value,
      anthropic: document.getElementById('anthropic-key').value
    };
    
    // TODO: Send to voice service config endpoint
    console.log('Saving settings:', keys);
    
    this.settingsModal.classList.add('hidden');
  }
  
  updateConnectionStatus(status, message) {
    const dot = this.connectionStatus.querySelector('.status-dot');
    const text = this.connectionStatus.querySelector('span:last-child');
    
    dot.className = 'status-dot ' + status;
    text.textContent = message;
  }
  
  async connect() {
    this.serverUrl = this.serverUrlInput.value;
    this.updateConnectionStatus('connecting', 'Connecting...');
    
    try {
      // First check health endpoint
      const response = await fetch(`${this.serverUrl}/health`);
      if (!response.ok) throw new Error('Server not responding');
      
      const health = await response.json();
      console.log('Server health:', health);
      
      // Get providers
      await this.loadProviders();
      
      // Connect WebSocket
      this.connectWebSocket();
      
    } catch (error) {
      console.error('Connection failed:', error);
      this.updateConnectionStatus('disconnected', 'Connection failed');
      this.addStatusMessage('Failed to connect to Voice Service. Is it running?');
    }
  }
  
  connectWebSocket() {
    const wsUrl = this.serverUrl.replace('http', 'ws') + '/ws/voice';
    
    this.ws = new WebSocket(wsUrl);
    
    this.ws.onopen = () => {
      this.isConnected = true;
      this.updateConnectionStatus('connected', 'Connected');
      this.micBtn.disabled = false;
      this.addStatusMessage('Connected to Voice Service');
      
      // Send initial TTS settings
      this.sendTTSSettings();
    };
    
    this.ws.onclose = () => {
      this.isConnected = false;
      this.updateConnectionStatus('disconnected', 'Disconnected');
      this.micBtn.disabled = true;
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.updateConnectionStatus('disconnected', 'Error');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleWebSocketMessage(data);
    };
  }
  
  handleWebSocketMessage(data) {
    switch (data.type) {
      case 'status':
        this.addStatusMessage(data.message);
        break;
        
      case 'transcription':
        this.addMessage('user', data.text);
        break;
        
      case 'response':
        this.addMessage('assistant', data.text);
        break;
        
      case 'audio':
        this.playAudio(data.audio_base64);
        break;
    }
  }
  
  async loadProviders() {
    try {
      const response = await fetch(`${this.serverUrl}/llm/providers`);
      const data = await response.json();
      
      this.providers = data.providers;
      this.activeProvider = data.active_provider;
      this.activeModel = data.active_model;
      
      // Update provider select
      this.providerSelect.value = this.activeProvider;
      
      // Load models for active provider
      this.updateModelSelect();
      
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  }
  
  updateModelSelect() {
    const provider = this.providers[this.activeProvider];
    if (!provider) return;
    
    this.modelSelect.innerHTML = '';
    provider.models.forEach(model => {
      const option = document.createElement('option');
      option.value = model;
      option.textContent = model.split('/').pop(); // Show short name
      if (model === this.activeModel) {
        option.selected = true;
      }
      this.modelSelect.appendChild(option);
    });
  }
  
  async selectProvider(provider) {
    this.activeProvider = provider;
    this.updateModelSelect();
    
    // Set first model as active
    const models = this.providers[provider]?.models || [];
    if (models.length > 0) {
      await this.selectModel(models[0]);
    }
  }
  
  async selectModel(model) {
    this.activeModel = model;
    
    try {
      await fetch(`${this.serverUrl}/llm/set-active?provider=${this.activeProvider}&model=${model}`, {
        method: 'POST'
      });
      this.addStatusMessage(`Switched to ${model.split('/').pop()}`);
    } catch (error) {
      console.error('Failed to set model:', error);
    }
  }
  
  sendTTSSettings() {
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify({
        type: 'settings',
        exaggeration: this.ttsSettings.exaggeration,
        temperature: this.ttsSettings.temperature,
        cfg_weight: this.ttsSettings.cfgWeight
      }));
    }
  }
  
  async startRecording() {
    if (this.isRecording || !this.isConnected) return;
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.audioChunks = [];
      
      this.mediaRecorder.ondataavailable = (event) => {
        this.audioChunks.push(event.data);
      };
      
      this.mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        await this.sendAudio(audioBlob);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };
      
      this.mediaRecorder.start();
      this.isRecording = true;
      this.micBtn.classList.add('recording');
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      this.addStatusMessage('Microphone access denied');
    }
  }
  
  stopRecording() {
    if (!this.isRecording || !this.mediaRecorder) return;
    
    this.mediaRecorder.stop();
    this.isRecording = false;
    this.micBtn.classList.remove('recording');
  }
  
  async sendAudio(audioBlob) {
    // Convert to base64
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1];
      
      if (this.ws && this.isConnected) {
        this.ws.send(JSON.stringify({
          type: 'audio',
          audio_base64: base64,
          language: null // Auto-detect
        }));
      }
    };
    reader.readAsDataURL(audioBlob);
  }
  
  async sendTextMessage() {
    const text = this.textInput.value.trim();
    if (!text) return;
    
    this.textInput.value = '';
    this.textInput.style.height = 'auto';
    
    if (this.ws && this.isConnected) {
      // Send via WebSocket for full voice response
      this.ws.send(JSON.stringify({
        type: 'text',
        text: text,
        synthesize: true // Request TTS for response
      }));
      this.addMessage('user', text);
    } else {
      // Fallback to REST API
      await this.sendTextViaRest(text);
    }
  }
  
  async sendTextViaRest(text) {
    this.addMessage('user', text);
    this.addStatusMessage('Thinking...');
    
    try {
      const response = await fetch(`${this.serverUrl}/llm/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{ role: 'user', content: text }]
        })
      });
      
      const data = await response.json();
      this.addMessage('assistant', data.response);
      
    } catch (error) {
      console.error('Chat failed:', error);
      this.addStatusMessage('Failed to get response');
    }
  }
  
  addMessage(role, content) {
    // Remove welcome message if present
    const welcome = this.chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.textContent = content;
    
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
  }
  
  addStatusMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message status';
    messageDiv.textContent = message;
    
    this.chatMessages.appendChild(messageDiv);
    this.scrollToBottom();
    
    // Auto-remove status messages after 3 seconds
    setTimeout(() => {
      if (messageDiv.parentNode) {
        messageDiv.remove();
      }
    }, 3000);
  }
  
  playAudio(base64Audio) {
    const audio = new Audio(`data:audio/wav;base64,${base64Audio}`);
    audio.play().catch(e => console.error('Audio playback failed:', e));
  }
  
  scrollToBottom() {
    this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
  }
  
  clearChat() {
    // Clear UI
    this.chatMessages.innerHTML = `
      <div class="welcome-message">
        <h2>👋 Welcome to Voice Chat</h2>
        <p>Click the microphone button or type a message to start chatting.</p>
        <p class="hint">Make sure the Voice Service is running on port 8765.</p>
      </div>
    `;
    
    // Clear server-side history
    if (this.ws && this.isConnected) {
      this.ws.send(JSON.stringify({ type: 'clear' }));
    }
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.voiceChat = new VoiceChat();
});
