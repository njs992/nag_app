# Architecture Plan: Online Tabletop RPG Platform

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER (Python)                   │
│         Flask/FastAPI + WebSocket (Real-time Hub)            │
│  - REST API (game logic, authentication, data management)     │
│  - WebSocket server (live player updates, GM broadcasts)      │
│  - Feature modules (modular game mechanics)                   │
│  - JSON file storage (game state, configs, maps, characters)  │
└─────────────────────────────────────────────────────────────┘
          ↑                              ↑
          │ WebSocket + REST API        │ WebSocket + REST API
          │                              │
    ┌─────────────┐              ┌──────────────────┐
    │ PLAYER WEB  │              │  GM DESKTOP APP  │
    │  (Browser)  │              │     (PyQt)       │
    │             │              │                  │
    │ • Character │              │ • Full control   │
    │   info pane │              │ • Map editing    │
    │ • Gameboard │              │ • NPC control    │
    │ • Controls  │              │ • Advanced UI    │
    └─────────────┘              └──────────────────┘
    (HTML/CSS/JS)                  (Desktop GUI)
```

---

## Project Structure

```
nag_app/
├── server_setup/                   # This folder - planning docs
├── backend/
│   ├── app.py                     # Main Flask/FastAPI app
│   ├── config.py                  # Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── features/                  # Modular feature packages
│   │   ├── __init__.py
│   │   ├── characters.py          # Character management
│   │   ├── gameboard.py           # Map/board logic
│   │   ├── combat.py              # Combat system
│   │   ├── inventory.py           # Item/loot system
│   │   ├── npcs.py                # NPC management
│   │   ├── spells_abilities.py    # Spells/abilities
│   │   └── ...
│   ├── api/                       # REST API routes
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── game.py
│   │   ├── players.py
│   │   └── ...
│   ├── websocket/                 # WebSocket handlers
│   │   ├── __init__.py
│   │   ├── events.py              # Event broadcasting
│   │   └── handlers.py            # Connection handling
│   └── data/                      # JSON data files
│       ├── games/                 # Campaign data
│       ├── characters/            # Character sheets
│       ├── maps/                  # Game maps
│       ├── config.json            # Server config
│       └── ...
│
├── gm_app/                        # PyQt Desktop App
│   ├── main.py                   # Entry point
│   ├── config.py                 # App config
│   ├── ui/                       # UI components
│   │   ├── main_window.py
│   │   ├── map_editor.py
│   │   ├── character_panel.py
│   │   ├── npc_panel.py
│   │   └── ...
│   ├── api_client.py             # Backend API client
│   └── websocket_client.py       # WebSocket connection
│
├── player_web/                    # Web frontend served by backend
│   ├── templates/
│   │   ├── index.html
│   │   ├── character.html
│   │   └── gameboard.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── gameboard.css
│   │   ├── js/
│   │   │   ├── api_client.js
│   │   │   ├── websocket_client.js
│   │   │   ├── gameboard.js
│   │   │   └── character.js
│   │   └── assets/
│   │       └── (images, icons, etc)
│   └── index.html (served as root)
│
└── README.md                      # Project overview
```

---

## Data Storage Strategy (JSON Files)

All game data stored as JSON for easy editing and version control.

### Game State Structure
```
data/games/
├── campaign_001/
│   ├── game.json              # Campaign metadata
│   ├── characters/
│   │   ├── player_1.json
│   │   ├── player_2.json
│   │   └── ...
│   ├── npcs.json              # Non-player characters
│   ├── current_map.json       # Active gameboard state
│   ├── maps/
│   │   ├── town_square.json
│   │   ├── dungeon_level_1.json
│   │   └── ...
│   └── history.json           # Turn log, events
```

### Example: Character Data (character.json)
```json
{
  "id": "player_1",
  "player_name": "Sarah",
  "character_name": "Aragorn",
  "class": "Ranger",
  "level": 5,
  "stats": {
    "str": 16,
    "dex": 14,
    "con": 15,
    "int": 12,
    "wis": 13,
    "cha": 11
  },
  "position": {"x": 10, "y": 8},
  "inventory": ["sword", "bow", "torch"],
  "health": {"current": 25, "max": 25},
  "abilities": ["rapid_shot", "survival"]
}
```

---

## Real-Time Communication

### WebSocket Events

**Player → Backend:**
- `move_character` – player moves on gameboard
- `use_ability` – cast spell / use ability
- `chat_message` – in-game chat
- `update_character` – modify own character

**GM → Backend:**
- `move_npc` – control NPC
- `modify_map` – add/remove/edit map objects
- `spawn_enemy` – add enemy to board
- `roll_result` – send dice roll to all players
- `game_event` – broadcast narrative/story event

**Backend → All Clients (Broadcasting):**
- `character_moved` – player X moved to Y,Z
- `npc_moved` – NPC moved
- `game_state_update` – any state change
- `chat_message` – message from another player
- `combat_initiated` – turn order, stats
- `map_changed` – map modified by GM

---

## Feature Modules (Modular Design)

### Core Modules to Implement
1. **characters** – Create, load, save, stats
2. **gameboard** – Map rendering, collision, positioning
3. **combat** – Initiative, turn order, damage
4. **inventory** – Item management
5. **npcs** – Non-player character behaviors
6. **spells_abilities** – Spell/ability execution
7. **dice** – Randomization for rolls
8. **auth** – Player authentication / session management
9. **game_state** – Central game state management
10. **networking** – WebSocket utilities

Each module is **self-contained**, with:
- Clear input/output (functions)
- No direct UI coupling
- Testable in isolation
- Easy to add/modify features

---

## Development Phases

### Phase 1: Backend Foundation
- [ ] Flask/FastAPI server setup
- [ ] WebSocket integration
- [ ] JSON file I/O system
- [ ] Basic REST API endpoints
- [ ] Character module
- [ ] Gameboard module

### Phase 2: Player Web Interface
- [ ] Character panel UI
- [ ] Gameboard rendering
- [ ] WebSocket client connection
- [ ] Real-time updates

### Phase 3: GM Desktop App
- [ ] PyQt window setup
- [ ] API client library
- [ ] Map editor UI
- [ ] NPC control panel
- [ ] Broadcasting controls

### Phase 4: Advanced Features
- [ ] Combat system
- [ ] Inventory management
- [ ] Spell/ability system
- [ ] Advanced NPC behaviors

### Phase 5: Polish & Testing
- [ ] Error handling
- [ ] Performance optimization
- [ ] Documentation
- [ ] User testing with 5 clients

---

## Dependencies

### Backend
- Flask or FastAPI (web framework)
- python-socketio (WebSockets)
- python-dotenv (config)

### GM App
- PyQt5 or PyQt6 (GUI)
- requests (HTTP client)
- websocket-client (WebSocket client)

### Player Web
- Vanilla JavaScript (or lightweight framework)
- Socket.IO client (WebSocket)

---

## Next Steps
1. Set up backend project structure
2. Create Flask/FastAPI skeleton with WebSocket
3. Implement character + gameboard modules
4. Build player web interface basics
5. Create GM app skeleton
