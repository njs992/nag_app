# WebSocket Event Protocol

## Real-Time Events for Tabletop RPG

This document defines all WebSocket events used for real-time communication between server and clients.

---

## Event Categories

### 1. Connection Events
- `connect` - Client connects to server
- `disconnect` - Client disconnects
- `player_joined` - New player joins game
- `player_left` - Player leaves game

### 2. Character Movement Events
- `character_moved` - Player moved character
- `npc_moved` - NPC moved
- `position_update` - Character position changed

### 3. Game State Events
- `game_state_update` - General game state change
- `map_changed` - Gameboard/map modified
- `enemy_spawned` - Enemy appeared on map
- `loot_spawned` - Loot/items appeared

### 4. Combat Events
- `combat_initiated` - Combat started
- `turn_order_update` - Initiative/turn order changed
- `attack_performed` - Player/NPC attacked
- `damage_taken` - Character took damage
- `character_defeated` - Character defeated

### 5. Chat & Communication
- `chat_message` - In-game chat message
- `system_message` - System notification
- `player_action` - Player used ability/spell

### 6. Character/NPC Events
- `character_updated` - Character stats/info changed
- `npc_action` - NPC performed action
- `dialogue_started` - NPC dialogue/interaction

### 7. GM Commands (Game Master only)
- `spawn_npc` - GM spawned NPC
- `spawn_enemy` - GM spawned enemy
- `modify_map` - GM modified map
- `broadcast_event` - GM broadcast narrative event
- `end_turn` - GM ended turn

---

## Event Format

### Client → Server
```json
{
  "event": "event_name",
  "data": {
    ...event specific data...
  }
}
```

### Server → Client (Broadcast)
```json
{
  "event": "event_name",
  "data": {
    ...event specific data...
  },
  "timestamp": 1234567890,
  "source": "server|player_id"
}
```

---

## Detailed Event Definitions

### Character Movement
**Client sends:**
```json
{
  "event": "move_character",
  "data": {
    "character_id": "player_1",
    "x": 15,
    "y": 20
  }
}
```

**Server broadcasts:**
```json
{
  "event": "character_moved",
  "data": {
    "character_id": "player_1",
    "old_position": {"x": 10, "y": 8},
    "new_position": {"x": 15, "y": 20},
    "player_name": "Sarah"
  },
  "timestamp": 1234567890
}
```

### Chat Message
**Client sends:**
```json
{
  "event": "chat_message",
  "data": {
    "text": "Let's attack the goblin!",
    "channel": "party"
  }
}
```

**Server broadcasts:**
```json
{
  "event": "chat_message",
  "data": {
    "player_id": "player_1",
    "player_name": "Sarah",
    "text": "Let's attack the goblin!",
    "channel": "party"
  },
  "timestamp": 1234567890
}
```

### Combat Started
**Server broadcasts (GM initiated):**
```json
{
  "event": "combat_initiated",
  "data": {
    "combat_id": "combat_001",
    "participants": [
      {"id": "player_1", "name": "Aragorn", "turn_order": 1},
      {"id": "enemy_1", "name": "Goblin Warrior", "turn_order": 2}
    ],
    "current_turn": "player_1"
  }
}
```

### Map Changed
**Server broadcasts (GM modified):**
```json
{
  "event": "map_changed",
  "data": {
    "map_name": "Dungeon Level 1",
    "changes": [
      {"x": 5, "y": 5, "type": "door", "state": "open"},
      {"x": 10, "y": 8, "type": "treasure", "visible": true}
    ]
  }
}
```

### NPC Action
**Server broadcasts:**
```json
{
  "event": "npc_action",
  "data": {
    "npc_id": "goblin_1",
    "action": "cast_spell",
    "target": "player_1",
    "spell": "fireball",
    "damage": 15
  }
}
```

---

## Event Handler Priority

1. **Connection Events** - Handle immediately
2. **Combat Events** - High priority
3. **Movement Events** - High priority  
4. **Chat Messages** - Normal priority
5. **Status Updates** - Low priority

---

## Reliability & Ordering

- All events include timestamps
- Events processed in order received
- Critical events (combat, damage) require ACK
- Non-critical events (chat) can be lost without harm

---

## Security Considerations

- Validate all client events on server
- Only players can move their own characters
- Only GM can use GM commands
- Prevent rapid-fire spam (rate limiting)
- Sanitize text inputs (chat)
