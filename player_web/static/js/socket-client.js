/**
 * Tabletop RPG Socket.IO Client
 * 
 * Manages real-time WebSocket communication with the backend server.
 * Handles connection, disconnection, and all game events.
 */

class RPGSocketClient {
    constructor() {
        this.socket = null;
        this.playerId = null;
        this.characterId = null;
        this.characterName = null;
        this.isGM = false;
        this.connected = false;
        this.gameState = null;
        
        // Event listeners (callbacks)
        this.listeners = {};
    }
    
    /**
     * Connect to the server
     */
    connect() {
        console.log('[SOCKET] Connecting to server...');
        this.socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 5
        });
        
        this.registerSocketListeners();
    }
    
    /**
     * Register all Socket.IO event listeners
     */
    registerSocketListeners() {
        // Connection events
        this.socket.on('connect', () => this.onConnect());
        this.socket.on('disconnect', () => this.onDisconnect());
        this.socket.on('response', (data) => this.onResponse(data));
        this.socket.on('error', (data) => this.onError(data));
        
        // Player events
        this.socket.on('player_joined', (data) => this.onPlayerJoined(data));
        this.socket.on('player_left', (data) => this.onPlayerLeft(data));
        
        // Movement events
        this.socket.on('character_moved', (data) => this.onCharacterMoved(data));
        
        // Chat events
        this.socket.on('chat_message', (data) => this.onChatMessage(data));
        
        // Combat events
        this.socket.on('combat_initiated', (data) => this.onCombatInitiated(data));
        this.socket.on('combat_ended', (data) => this.onCombatEnded(data));
        this.socket.on('turn_advanced', (data) => this.onTurnAdvanced(data));
        
        // Gameboard events
        this.socket.on('map_loaded', (data) => this.onMapLoaded(data));
        
        // State sync events
        this.socket.on('game_state_update', (data) => this.onGameStateUpdate(data));
        
        // Echo test
        this.socket.on('echo_response', (data) => this.onEchoResponse(data));
    }
    
    /**
     * Subscribe to a client-side event
     */
    on(eventName, callback) {
        if (!this.listeners[eventName]) {
            this.listeners[eventName] = [];
        }
        this.listeners[eventName].push(callback);
    }
    
    /**
     * Emit a client-side event
     */
    emit(eventName, data) {
        if (!this.listeners[eventName]) {
            return;
        }
        this.listeners[eventName].forEach(callback => callback(data));
    }
    
    // ========== Connection Events ==========
    
    onConnect() {
        console.log('[SOCKET] Connected to server');
        this.connected = true;
        this.emit('connected');
    }
    
    onDisconnect() {
        console.log('[SOCKET] Disconnected from server');
        this.connected = false;
        this.emit('disconnected');
    }
    
    onResponse(data) {
        console.log('[SOCKET] Server response:', data);
        this.emit('response', data);
    }
    
    onError(data) {
        console.error('[SOCKET] Error:', data);
        this.emit('error', data);
    }
    
    // ========== Player Events ==========
    
    /**
     * Join game with character
     */
    joinGame(characterName, characterId, isGM = false) {
        this.characterName = characterName;
        this.characterId = characterId;
        this.isGM = isGM;
        
        if (!this.playerId) {
            this.playerId = this.generatePlayerId();
        }
        
        console.log(`[GAME] ${characterName} joining as ${isGM ? 'GM' : 'Player'}`);
        
        this.socket.emit('player_join', {
            player_id: this.playerId,
            character_id: characterId,
            character_name: characterName,
            is_gm: isGM
        });
    }
    
    onPlayerJoined(data) {
        console.log('[GAME] Player joined:', data);
        this.emit('player_joined', data);
    }
    
    onPlayerLeft(data) {
        console.log('[GAME] Player left:', data);
        this.emit('player_left', data);
    }
    
    // ========== Movement Events ==========
    
    /**
     * Send character movement
     */
    moveCharacter(x, y) {
        if (!this.playerId) {
            console.warn('[GAME] Not joined - cannot move');
            return;
        }
        
        console.log(`[MOVE] Moving to (${x}, ${y})`);
        
        this.socket.emit('move_character', {
            player_id: this.playerId,
            x: x,
            y: y
        });
    }
    
    onCharacterMoved(data) {
        console.log('[GAME] Character moved:', data);
        this.emit('character_moved', data);
    }
    
    // ========== Chat Events ==========
    
    /**
     * Send chat message
     */
    sendChatMessage(text, channel = 'party') {
        if (!this.playerId) {
            console.warn('[CHAT] Not joined - cannot chat');
            return;
        }
        
        console.log(`[CHAT] ${channel}: ${text}`);
        
        this.socket.emit('chat_message', {
            player_id: this.playerId,
            text: text,
            channel: channel
        });
    }
    
    onChatMessage(data) {
        console.log('[CHAT] Message:', data);
        this.emit('chat_message', data);
    }
    
    // ========== Combat Events ==========
    
    /**
     * Request combat start (GM only)
     */
    requestCombat(participants) {
        if (!this.isGM) {
            console.warn('[COMBAT] Only GM can request combat');
            return;
        }
        
        console.log('[COMBAT] Requesting combat start with participants:', participants);
        
        this.socket.emit('request_combat', {
            player_id: this.playerId,
            participants: participants
        });
    }
    
    onCombatInitiated(data) {
        console.log('[COMBAT] Combat initiated:', data);
        this.emit('combat_initiated', data);
    }
    
    /**
     * End combat (GM only)
     */
    endCombat() {
        if (!this.isGM) {
            console.warn('[COMBAT] Only GM can end combat');
            return;
        }
        
        console.log('[COMBAT] Requesting combat end');
        
        this.socket.emit('end_combat', {
            player_id: this.playerId
        });
    }
    
    onCombatEnded(data) {
        console.log('[COMBAT] Combat ended:', data);
        this.emit('combat_ended', data);
    }
    
    /**
     * Advance turn in combat (GM only)
     */
    nextTurn() {
        if (!this.isGM) {
            console.warn('[COMBAT] Only GM can advance turns');
            return;
        }
        
        console.log('[COMBAT] Advancing turn');
        
        this.socket.emit('next_turn', {
            player_id: this.playerId
        });
    }
    
    onTurnAdvanced(data) {
        console.log('[COMBAT] Turn advanced:', data);
        this.emit('turn_advanced', data);
    }
    
    // ========== Gameboard Events ==========
    
    /**
     * Load map (GM only)
     */
    loadMap(mapName) {
        if (!this.isGM) {
            console.warn('[MAP] Only GM can load maps');
            return;
        }
        
        console.log(`[MAP] Loading map: ${mapName}`);
        
        this.socket.emit('load_map', {
            player_id: this.playerId,
            map_name: mapName
        });
    }
    
    onMapLoaded(data) {
        console.log('[MAP] Map loaded:', data);
        this.emit('map_loaded', data);
    }
    
    // ========== State Sync Events ==========
    
    /**
     * Request current game state
     */
    requestGameState() {
        console.log('[STATE] Requesting game state');
        
        this.socket.emit('request_game_state', {
            player_id: this.playerId
        });
    }
    
    onGameStateUpdate(data) {
        console.log('[STATE] Game state updated:', data);
        this.gameState = data.state;
        this.emit('game_state_update', data);
    }
    
    // ========== Utility Events ==========
    
    /**
     * Send echo test message
     */
    echo(message) {
        console.log(`[ECHO] Sending: ${message}`);
        
        this.socket.emit('echo', {
            player_id: this.playerId,
            message: message
        });
    }
    
    onEchoResponse(data) {
        console.log('[ECHO] Response:', data);
        this.emit('echo_response', data);
    }
    
    // ========== Utility Methods ==========
    
    /**
     * Generate unique player ID
     */
    generatePlayerId() {
        return `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Check if connected
     */
    isConnected() {
        return this.connected && this.socket && this.socket.connected;
    }
    
    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
    
    /**
     * Get current session info
     */
    getSessionInfo() {
        return {
            playerId: this.playerId,
            characterId: this.characterId,
            characterName: this.characterName,
            isGM: this.isGM,
            connected: this.isConnected()
        };
    }
}

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RPGSocketClient;
}
