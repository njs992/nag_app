/**
 * Tabletop RPG Player Web Interface
 * 
 * Main application logic for the player web interface
 */

let socket = null;
let gameState = {
    player: null,
    gameboard: null,
    players: [],
    combatActive: false
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('[APP] Initializing RPG Player Interface');
    
    initializeSocket();
    attachEventListeners();
    updateStatus('Disconnected', false);
});

function initializeSocket() {
    socket = new RPGSocketClient();
    
    // Set up client-side event listeners
    socket.on('connected', onSocketConnected);
    socket.on('disconnected', onSocketDisconnected);
    socket.on('error', onSocketError);
    
    socket.on('player_joined', onPlayerJoined);
    socket.on('character_moved', onCharacterMoved);
    socket.on('chat_message', onChatMessage);
    socket.on('game_state_update', onGameStateUpdate);
    socket.on('map_loaded', onMapLoaded);
    socket.on('combat_initiated', onCombatInitiated);
    socket.on('combat_ended', onCombatEnded);
    socket.on('turn_advanced', onTurnAdvanced);
    
    // Connect to server
    socket.connect();
}

function attachEventListeners() {
    // Join game button
    const joinBtn = document.getElementById('join-btn');
    if (joinBtn) {
        joinBtn.addEventListener('click', handleJoinGame);
    }
    
    // Chat form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }
    
    // Movement controls
    const moveButtons = document.querySelectorAll('.move-btn');
    moveButtons.forEach(btn => {
        btn.addEventListener('click', handleMovement);
    });
}

// ============================================================================
// SOCKET EVENTS
// ============================================================================

function onSocketConnected() {
    console.log('[APP] Connected to server');
    updateStatus('Connected', true);
    
    // Show join form
    const joinSection = document.getElementById('join-section');
    if (joinSection) {
        joinSection.style.display = 'block';
    }
}

function onSocketDisconnected() {
    console.log('[APP] Disconnected from server');
    updateStatus('Disconnected', false);
    gameState.player = null;
}

function onSocketError(data) {
    console.error('[APP] Socket error:', data);
    showNotification('Error: ' + (data.message || 'Unknown error'), 'error');
}

function onPlayerJoined(data) {
    console.log('[APP] Player joined:', data);
    
    if (data.character_name === gameState.player.characterName) {
        // This is us - game confirmed
        showNotification(`Welcome, ${data.character_name}!`, 'success');
    } else {
        // Another player joined
        showNotification(`${data.character_name} joined the game`, 'info');
    }
    
    // Update game state
    socket.requestGameState();
}

function onCharacterMoved(data) {
    console.log('[APP] Character moved:', data);
    
    // Update player list or UI
    const playerList = document.getElementById('player-list');
    if (playerList) {
        addOrUpdatePlayer(data.character_name, data.new_position);
    }
    
    // Show notification (only if not us)
    if (data.player_id !== socket.playerId) {
        showNotification(`${data.character_name} moved`, 'info');
    }
}

function onChatMessage(data) {
    console.log('[APP] Chat message:', data);
    
    const chatOutput = document.getElementById('chat-output');
    if (chatOutput) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message';
        msgDiv.innerHTML = `<strong>${data.player_name}:</strong> ${escapeHtml(data.text)}`;
        
        chatOutput.appendChild(msgDiv);
        chatOutput.scrollTop = chatOutput.scrollHeight;
    }
}

function onGameStateUpdate(data) {
    console.log('[APP] Game state updated:', data);
    gameState = data.state;
    
    // Update UI with new state
    updateGameboardInfo();
    updatePlayerList();
}

function onMapLoaded(data) {
    console.log('[APP] Map loaded:', data);
    showNotification(`Map loaded: ${data.map_name} (${data.width}x${data.height})`, 'success');
    
    // Update gameboard display
    const boardInfo = document.getElementById('board-info');
    if (boardInfo) {
        boardInfo.innerHTML = `
            <strong>Map:</strong> ${data.map_name}<br/>
            <strong>Size:</strong> ${data.width} x ${data.height}
        `;
    }
}

function onCombatInitiated(data) {
    console.log('[APP] Combat initiated:', data);
    gameState.combatActive = true;
    
    showNotification('Combat started!', 'warning');
    
    // Show combat info
    const combatInfo = document.getElementById('combat-info');
    if (combatInfo) {
        combatInfo.innerHTML = `
            <strong>Combat Active</strong><br/>
            <strong>Round:</strong> 1<br/>
            <strong>Participants:</strong> ${data.participants.length}
        `;
        combatInfo.style.display = 'block';
    }
}

function onCombatEnded(data) {
    console.log('[APP] Combat ended:', data);
    gameState.combatActive = false;
    
    showNotification(`Combat ended after ${data.total_rounds} rounds`, 'info');
    
    // Hide combat info
    const combatInfo = document.getElementById('combat-info');
    if (combatInfo) {
        combatInfo.style.display = 'none';
    }
}

function onTurnAdvanced(data) {
    console.log('[APP] Turn advanced:', data);
    showNotification(`Round ${data.round} - Turn for next participant`, 'info');
}

// ============================================================================
// USER ACTIONS
// ============================================================================

function handleJoinGame() {
    const nameInput = document.getElementById('character-name-input');
    const characterName = nameInput ? nameInput.value.trim() : 'Unknown';
    
    if (!characterName) {
        showNotification('Please enter a character name', 'error');
        return;
    }
    
    const characterId = `char_${Math.random().toString(36).substr(2, 9)}`;
    const isGM = false; // Web players are not GMs (that's the desktop app)
    
    gameState.player = {
        characterName: characterName,
        characterId: characterId,
        isGM: isGM
    };
    
    socket.joinGame(characterName, characterId, isGM);
    
    // Hide join form
    const joinSection = document.getElementById('join-section');
    if (joinSection) {
        joinSection.style.display = 'none';
    }
    
    // Show game interface
    const gameSection = document.getElementById('game-section');
    if (gameSection) {
        gameSection.style.display = 'flex';
    }
}

function handleChatSubmit(event) {
    event.preventDefault();
    
    const input = document.getElementById('chat-input');
    const text = input ? input.value.trim() : '';
    
    if (!text) return;
    
    socket.sendChatMessage(text, 'party');
    
    // Clear input
    if (input) {
        input.value = '';
        input.focus();
    }
}

function handleMovement(event) {
    const btn = event.target;
    const direction = btn.dataset.direction;
    
    if (!socket.isConnected()) {
        showNotification('Not connected', 'error');
        return;
    }
    
    // This is a simple test - real implementation would track current position
    const directionMap = {
        'up': { dx: 0, dy: -1 },
        'down': { dx: 0, dy: 1 },
        'left': { dx: -1, dy: 0 },
        'right': { dx: 1, dy: 0 }
    };
    
    const dir = directionMap[direction];
    if (!dir) return;
    
    // In real implementation, track current position
    // For now, just send a test move
    socket.moveCharacter(10 + dir.dx * 5, 10 + dir.dy * 5);
}

// ============================================================================
// UI UPDATES
// ============================================================================

function updateStatus(message, connected) {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
        statusEl.textContent = message;
        statusEl.className = 'status ' + (connected ? 'connected' : 'disconnected');
    }
}

function updateGameboardInfo() {
    const boardInfo = document.getElementById('board-info');
    if (boardInfo && gameState.gameboard) {
        boardInfo.innerHTML = `
            <strong>Map:</strong> ${gameState.gameboard.map_name}<br/>
            <strong>Size:</strong> ${gameState.gameboard.width} x ${gameState.gameboard.height}
        `;
    }
}

function updatePlayerList() {
    const playerList = document.getElementById('player-list');
    if (!playerList) return;
    
    playerList.innerHTML = '';
    
    if (gameState.players && gameState.players.length > 0) {
        gameState.players.forEach(player => {
            const li = document.createElement('li');
            li.innerHTML = `
                <strong>${player.character_name}</strong><br/>
                Position: (${player.position.x}, ${player.position.y})
            `;
            playerList.appendChild(li);
        });
    }
}

function addOrUpdatePlayer(name, position) {
    const playerList = document.getElementById('player-list');
    if (!playerList) return;
    
    // Simple update - find existing or add
    let li = Array.from(playerList.querySelectorAll('li'))
        .find(el => el.textContent.includes(name));
    
    if (!li) {
        li = document.createElement('li');
        playerList.appendChild(li);
    }
    
    li.innerHTML = `
        <strong>${name}</strong><br/>
        Position: (${position.x}, ${position.y})
    `;
}

function showNotification(message, type = 'info') {
    console.log(`[NOTIFY] ${type.toUpperCase()}: ${message}`);
    
    const notifications = document.getElementById('notifications');
    if (notifications) {
        const div = document.createElement('div');
        div.className = `notification ${type}`;
        div.textContent = message;
        
        notifications.appendChild(div);
        
        // Auto-remove after 5 seconds
        setTimeout(() => div.remove(), 5000);
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
