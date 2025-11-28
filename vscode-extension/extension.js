/**
 * Voice Development Assistant - VS Code Extension
 * Provides voice-enabled coding with TTS/STT and Claude integration
 */

const vscode = require('vscode');
const WebSocket = require('ws');

let ws = null;
let isListening = false;
let statusBarItem = null;
let outputChannel = null;
let mediaRecorder = null;
let audioChunks = [];

/**
 * Extension activation
 */
function activate(context) {
    console.log('Voice Development Assistant is now active!');
    
    // Create output channel
    outputChannel = vscode.window.createOutputChannel('Voice Dev');
    
    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(mic) Voice: Off";
    statusBarItem.command = 'voice-dev.toggleVoice';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
    
    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('voice-dev.startListening', startListening),
        vscode.commands.registerCommand('voice-dev.stopListening', stopListening),
        vscode.commands.registerCommand('voice-dev.toggleVoice', toggleVoice),
        vscode.commands.registerCommand('voice-dev.askClaude', askClaude),
        vscode.commands.registerCommand('voice-dev.dictateCode', dictateCode)
    );
    
    // Connect to voice server
    connectToServer();
}

/**
 * Connect to WebSocket voice server
 */
function connectToServer() {
    const config = vscode.workspace.getConfiguration('voiceDev');
    const serverUrl = config.get('serverUrl', 'ws://localhost:8766');
    
    try {
        ws = new WebSocket(serverUrl);
        
        ws.on('open', () => {
            outputChannel.appendLine('Connected to voice server');
            vscode.window.showInformationMessage('Voice Development Assistant connected');
        });
        
        ws.on('message', handleServerMessage);
        
        ws.on('error', (error) => {
            outputChannel.appendLine(`WebSocket error: ${error.message}`);
            vscode.window.showErrorMessage('Voice server connection error');
        });
        
        ws.on('close', () => {
            outputChannel.appendLine('Disconnected from voice server');
            ws = null;
            // Attempt reconnection after 5 seconds
            setTimeout(connectToServer, 5000);
        });
    } catch (error) {
        outputChannel.appendLine(`Connection error: ${error.message}`);
        vscode.window.showErrorMessage('Failed to connect to voice server');
    }
}

/**
 * Handle messages from voice server
 */
function handleServerMessage(data) {
    try {
        const message = JSON.parse(data);
        
        switch (message.type) {
            case 'transcription':
                handleTranscription(message.text);
                break;
            
            case 'response_chunk':
                handleResponseChunk(message.text);
                break;
            
            case 'audio_response':
                handleAudioResponse(message.audio, message.text);
                break;
            
            case 'status':
                updateStatus(message.message);
                break;
            
            case 'error':
                vscode.window.showErrorMessage(`Voice error: ${message.message}`);
                break;
            
            case 'complete':
                onConversationComplete();
                break;
        }
    } catch (error) {
        outputChannel.appendLine(`Error handling message: ${error.message}`);
    }
}

/**
 * Handle transcription from voice server
 */
function handleTranscription(text) {
    const config = vscode.workspace.getConfiguration('voiceDev');
    const showTranscription = config.get('showTranscription', true);
    const autoTranscribe = config.get('autoTranscribe', true);
    
    outputChannel.appendLine(`Transcription: ${text}`);
    
    if (showTranscription) {
        vscode.window.showInformationMessage(`You said: ${text}`);
    }
    
    if (autoTranscribe) {
        insertTextAtCursor(text);
    }
}

/**
 * Handle response chunks from Claude
 */
function handleResponseChunk(text) {
    outputChannel.append(text);
}

/**
 * Handle complete audio response
 */
function handleAudioResponse(audioBase64, text) {
    outputChannel.appendLine(`\nClaude: ${text}`);
    // Audio playback would be handled by the browser/UI
    // In VS Code, we show the text response
    showClaudeResponse(text);
}

/**
 * Update status bar
 */
function updateStatus(message) {
    statusBarItem.text = `$(sync~spin) ${message}`;
}

/**
 * Show Claude's response in a new editor
 */
function showClaudeResponse(text) {
    vscode.workspace.openTextDocument({
        content: text,
        language: 'markdown'
    }).then(doc => {
        vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
    });
}

/**
 * Insert text at cursor position
 */
function insertTextAtCursor(text) {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
        editor.edit(editBuilder => {
            editBuilder.insert(editor.selection.active, text);
        });
    }
}

/**
 * Start listening for voice input
 */
async function startListening() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        vscode.window.showErrorMessage('Voice server not connected');
        return;
    }
    
    if (isListening) {
        return;
    }
    
    isListening = true;
    statusBarItem.text = "$(mic) Voice: Listening...";
    
    // Note: Actual audio recording would require browser APIs
    // This is a placeholder for the recording logic
    vscode.window.showInformationMessage('Voice recording started (implementation pending)');
}

/**
 * Stop listening for voice input
 */
function stopListening() {
    if (!isListening) {
        return;
    }
    
    isListening = false;
    statusBarItem.text = "$(mic) Voice: Off";
    
    // Stop recording and send audio to server
    vscode.window.showInformationMessage('Voice recording stopped');
}

/**
 * Toggle voice listening
 */
function toggleVoice() {
    if (isListening) {
        stopListening();
    } else {
        startListening();
    }
}

/**
 * Ask Claude a question via voice
 */
async function askClaude() {
    const question = await vscode.window.showInputBox({
        prompt: 'Ask Claude a question',
        placeHolder: 'What would you like to know?'
    });
    
    if (!question) {
        return;
    }
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        vscode.window.showErrorMessage('Voice server not connected');
        return;
    }
    
    // Send text message to Claude
    ws.send(JSON.stringify({
        type: 'text',
        text: question,
        synthesize: true
    }));
    
    updateStatus('Asking Claude...');
}

/**
 * Start dictation mode for code
 */
async function dictateCode() {
    vscode.window.showInformationMessage('Dictation mode activated - speak your code');
    await startListening();
}

/**
 * Handle conversation completion
 */
function onConversationComplete() {
    statusBarItem.text = "$(mic) Voice: Ready";
}

/**
 * Extension deactivation
 */
function deactivate() {
    if (ws) {
        ws.close();
    }
    if (statusBarItem) {
        statusBarItem.dispose();
    }
    if (outputChannel) {
        outputChannel.dispose();
    }
}

module.exports = {
    activate,
    deactivate
};
