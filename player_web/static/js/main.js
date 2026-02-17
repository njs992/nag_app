// WebSocket and API client for player interface

class RPGClient {
    constructor() {
        this.socket = null;
        this.statusElement = document.getElementById('status');
    }
    
    connect() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.setStatus('Connected', true);
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.setStatus('Disconnected', false);
        });
        
        this.socket.on('response', (data) => {
            console.log('Server response:', data);
        });
        
        this.socket.on('character_moved', (data) => {
            console.log('Character moved:', data);
            this.updateCharacterPosition(data);
        });
    }
    
    setStatus(message, connected) {
        this.statusElement.textContent = message;
        if (connected) {
            this.statusElement.classList.add('connected');
        } else {
            this.statusElement.classList.remove('connected');
        }
    }
    
    sendMessage(message) {
        if (this.socket) {
            this.socket.emit('chat_message', {text: message});
        }
    }
    
    updateCharacterPosition(data) {
        // Will be implemented when gameboard renderer is created
        console.log('Position update:', data);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const client = new RPGClient();
    client.connect();
    
    // Chat input handler
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value) {
            client.sendMessage(this.value);
            this.value = '';
        }
    });
});
