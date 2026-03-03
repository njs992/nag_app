# WebSocket Real-Time Event System

## Overview

This document describes the complete real-time WebSocket event system for the Tabletop RPG application. The system enables real-time communication between the backend server and multiple connected players.

## Architecture

### Components

1. **Backend Event Handler** (`features/websocket_events.py`)
   - Centralized handler for all Socket.IO events
   - Manages event routing and broadcasting
   - Integrates with game state manager

2. **Game State Manager** (`features/game_state.py`)
   - Maintains current game session state
   - Tracks connected players and their positions
   - Manages gameboard and combat state
   - Thread-safe player registry

3. **Frontend Socket Client** (`player_web/static/js/socket-client.js`)
   - RPGSocketClient class for server communication
   - Event emission and listening
   - Session management

4. **Frontend Application** (`player_web/static/js/main.js`)
   - Event handler callbacks
   - UI updates in response to events
   - User action handlers

## Event Flow

### Connection Flow

```
Browser → Connect to /api/
         → Socket.IO upgrade
         → emit 'connect'
         → Server broadcasts 'connected'
         ← Display join form
```

### Player Join Flow

```
Player fills form → joinGame(name, charId)
                 → emit 'player_join'
                 → Server: add player to state
                 → emit 'player_joined' (to joiner)
                 → broadcast 'player_joined' (to others)
                 → broadcast 'game_state_update'
                 ← All clients see new player
```

### Movement Flow

```
Player clicks arrow → moveCharacter(x, y)
                   → emit 'move_character'
                   → Server: validate & update state
                   → broadcast 'character_moved'
                   ← All players see movement
```

## Event Dictionary

### Connection Events

#### `connect` (Server → Client)
Sent when a client successfully connects.
```json
{
  "event": "response",
  "data": {
    "status": "connected",
    "message": "Connected to server. SID: ...",
    "timestamp": 1234567890
  }
}
```

#### `disconnect` (Server → All)
Sent when a client disconnects.
```json
{
  "event": "player_left",
  "data": {
    "player_id": "player_1",
    "timestamp": 1234567890
  }
}
```

### Player Events

#### `player_join` (Client → Server)
Client requests to join game with character.
```json
{
  "event": "player_join",
  "data": {
    "player_id": "player_1",
    "character_id": "char_1",
    "character_name": "Aragorn",
    "is_gm": false
  }
}
```

#### `player_joined` (Server → All)
Sent when player successfully joins.
```json
{
  "event": "player_joined",
  "data": {
    "player_id": "player_1",
    "character_name": "Aragorn",
    "position": {"x": 0, "y": 0},
    "timestamp": 1234567890
  }
}
```

### Movement Events

#### `move_character` (Client → Server)
Client sends character movement.
```json
{
  "event": "move_character",
  "data": {
    "player_id": "player_1",
    "x": 15,
    "y": 20
  }
}
```

#### `character_moved` (Server → All)
Sent when character moves.
```json
{
  "event": "character_moved",
  "data": {
    "player_id": "player_1",
    "character_name": "Aragorn",
    "old_position": {"x": 10, "y": 8},
    "new_position": {"x": 15, "y": 20},
    "timestamp": 1234567890
  }
}
```

### Chat Events

#### `chat_message` (Client → Server)
Client sends chat message.
```json
{
  "event": "chat_message",
  "data": {
    "player_id": "player_1",
    "text": "Let's attack!",
    "channel": "party"
  }
}
```

#### `chat_message` (Server → All)
Broadcast chat to all players.
```json
{
  "event": "chat_message",
  "data": {
    "player_id": "player_1",
    "player_name": "Aragorn",
    "text": "Let's attack!",
    "channel": "party",
    "timestamp": 1234567890
  }
}
```

### Combat Events

#### `request_combat` (Client → Server - GM only)
GM initiates combat.
```json
{
  "event": "request_combat",
  "data": {
    "player_id": "gm_1",
    "participants": [
      {"id": "player_1", "name": "Aragorn", "turn_order": 1},
      {"id": "enemy_1", "name": "Goblin", "turn_order": 2}
    ]
  }
}
```

#### `combat_initiated` (Server → All)
Combat started.
```json
{
  "event": "combat_initiated",
  "data": {
    "combat_id": "combat_abc123",
    "participants": [...],
    "current_turn": "player_1",
    "timestamp": 1234567890
  }
}
```

#### `next_turn` (Client → Server - GM only)
GM advances to next turn.
```json
{
  "event": "next_turn",
  "data": {
    "player_id": "gm_1"
  }
}
```

#### `turn_advanced` (Server → All)
Turn advanced in combat.
```json
{
  "event": "turn_advanced",
  "data": {
    "current_turn": "enemy_1",
    "round": 2,
    "timestamp": 1234567890
  }
}
```

#### `end_combat` (Client → Server - GM only)
GM ends combat.
```json
{
  "event": "end_combat",
  "data": {
    "player_id": "gm_1"
  }
}
```

#### `combat_ended` (Server → All)
Combat ended.
```json
{
  "event": "combat_ended",
  "data": {
    "combat_id": "combat_abc123",
    "total_rounds": 5,
    "timestamp": 1234567890
  }
}
```

### Gameboard Events

#### `load_map` (Client → Server - GM only)
GM loads a map.
```json
{
  "event": "load_map",
  "data": {
    "player_id": "gm_1",
    "map_name": "Dungeon Level 1"
  }
}
```

#### `map_loaded` (Server → All)
Map loaded and visible to all.
```json
{
  "event": "map_loaded",
  "data": {
    "map_name": "Dungeon Level 1",
    "width": 100,
    "height": 100,
    "timestamp": 1234567890
  }
}
```

### State Synchronization

#### `request_game_state` (Client → Server)
Player requests current game state.
```json
{
  "event": "request_game_state",
  "data": {
    "player_id": "player_1"
  }
}
```

#### `game_state_update` (Server → Requester)
Send complete game state to player.
```json
{
  "event": "game_state_update",
  "data": {
    "state": {
      "game_state": "exploration",
      "players": [
        {
          "id": "player_1",
          "character_name": "Aragorn",
          "position": {"x": 10, "y": 8},
          "character_id": "char_1"
        }
      ],
      "gameboard": {
        "map_name": "Dungeon",
        "width": 100,
        "height": 100
      },
      "in_combat": false,
      "combat": null
    },
    "timestamp": 1234567890
  }
}
```

## Frontend API Reference

### RPGSocketClient Class

```javascript
// Create client
const socket = new RPGSocketClient();

// Connect to server
socket.connect();

// Join game
socket.joinGame(characterName, characterId, isGM = false);

// Movement
socket.moveCharacter(x, y);

// Chat
socket.sendChatMessage(text, channel = 'party');

// Combat (GM only)
socket.requestCombat(participants);
socket.nextTurn();
socket.endCombat();

// Gameboard (GM only)
socket.loadMap(mapName);

// State
socket.requestGameState();

// Utility
socket.echo(message);
socket.isConnected();
socket.disconnect();
socket.getSessionInfo();

// Event Listening
socket.on('player_joined', (data) => { ... });
socket.on('character_moved', (data) => { ... });
socket.on('chat_message', (data) => { ... });
// ... and many more
```

## Backend API Reference

### WebSocketEventHandler Class

Register all handlers:
```python
handler = WebSocketEventHandler(sio)
```

Use in handlers:
```python
handler.broadcast_event(event_name, data)
handler.emit_to_player(player_id, event_name, data)
handler.get_connected_players()
handler.get_event_stats()
```

### GameStateManager Class

```python
# Player management
game_state_manager.add_player(player_id, character_id, character_name, is_gm)
game_state_manager.remove_player(player_id)
game_state_manager.get_player(player_id)
game_state_manager.get_all_players()

# Position tracking
game_state_manager.update_player_position(player_id, x, y)
game_state_manager.get_player_position(player_id)

# Game state
game_state_manager.set_game_state(state)
game_state_manager.get_game_state()

# Combat
game_state_manager.start_combat(combat_id, participants)
game_state_manager.end_combat()
game_state_manager.get_combat()
game_state_manager.next_turn()

# Gameboard
game_state_manager.initialize_gameboard(map_name, width, height)
game_state_manager.get_gameboard()
```

## Security Considerations

1. **Player Validation** - Only players can move their own characters
2. **GM Commands** - Only GMs can use GM-specific events
3. **Input Validation** - All data validated before processing
4. **Rate Limiting** - Can be added for spam prevention
5. **Text Sanitization** - Chat messages sanitized to prevent XSS

## Performance Notes

- HTTP polling fallback for WebSocket unavailability
- Broadcast batching for efficiency
- Position validation before state update
- Turn-based combat prevents rapid events
- Player registry enables fast lookups

## Debugging

Enable console logging in browser:
```javascript
socket.on('connected', () => console.log('Connected'));
socket.on('character_moved', (data) => console.log('Moved:', data));
// ... etc
```

Check server logs for event flow.

## Future Enhancements

1. **Ability System** - Support for spells/abilities
2. **Damage Tracking** - Send damage/healing events
3. **Character Status** - Health, status effects
4. **Inventory** - Items and equipment changes
5. **NPC Behaviors** - NPC-specific events
6. **Fog of War** - Selective visibility
7. **Persistence** - Save/load game sessions
