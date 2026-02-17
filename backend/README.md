# Backend Server - Phase 1

## Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure (Optional)
```bash
cp .env.example .env
# Edit .env if needed (defaults work fine for local development)
```

### 3. Run Server
```bash
python app.py
```

Server will start on `http://127.0.0.1:5000`

---

## API Endpoints

### Health Check
```
GET /api/health
```
Response: `{"status": "ok", "message": "Backend is running"}`

### Get Server Config
```
GET /api/config
```
Response: `{"grid_size": 50, "max_players": 10}`

### Player Web Interface
```
GET /
```
Serves the player browser interface

---

## WebSocket Events

### Server → Client
- `response` – Test response from server
- `character_moved` – Character position update
- `game_state_update` – Any game state change

### Client → Server
- `echo` – Test echo message
- `chat_message` – Send chat message
- `move_character` – Move player character (to be implemented)

---

## Features Implemented (Phase 1)

✅ Flask app with WebSocket support  
✅ Character management module (save/load)  
✅ Gameboard module (map creation/editing)  
✅ Basic REST API  
✅ WebSocket connection setup  
✅ Player web interface skeleton  
✅ Configuration system  
✅ JSON file storage  

---

## File Structure

```
backend/
├── app.py                  # Main Flask app (WebSocket)
├── config.py              # Server configuration
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment config
├── features/
│   ├── characters.py     # Character management
│   └── gameboard.py      # Map/board management
├── api/                  # REST API routes (future)
├── websocket/            # WebSocket handlers (future)
└── data/                 # Game data storage
    ├── games/            # Campaign data
    ├── maps/             # Map files
    └── characters/       # Character files
```

---

## Next: Testing the Server

Run the test script to verify everything works:
```bash
python test_backend.py
```

This will:
- Test character creation/saving
- Test gameboard creation/saving
- Verify file storage
- Show all features are working
