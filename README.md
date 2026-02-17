# Tabletop RPG Platform

An online platform for running tabletop RPG campaigns with real-time multiplayer gameplay. Players join through a web browser, while the Game Master controls the action from a desktop application.

## Architecture

- **Backend**: Python Flask server with WebSocket real-time communication
- **Player Interface**: Web browser with gameboard and character controls
- **GM Interface**: PyQt desktop application (remote accessible)
- **Data Storage**: JSON files for campaigns, characters, maps, and configs

For detailed architecture, see [server_setup/ARCHITECTURE_PLAN.md](server_setup/ARCHITECTURE_PLAN.md)

## Quick Start

### Backend (Phase 1 - Complete ✓)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Server runs on `http://127.0.0.1:5000`

**Features:**
- ✓ Flask + WebSocket real-time communication
- ✓ Character creation, loading, and saving (JSON)
- ✓ Gameboard/map management
- ✓ Player web interface skeleton
- ✓ Modular feature design

### Test the Backend
```bash
cd backend
python test_backend.py
```

### Remote Access (Cloudflare Tunnel)

See [server_setup/REMOTE_ACCESS_GUIDE.md](server_setup/REMOTE_ACCESS_GUIDE.md) for instructions on making the app accessible to remote clients.

---

## Project Structure

```
nag_app/
├── server_setup/              # Planning & documentation
│   ├── REMOTE_ACCESS_GUIDE.md
│   └── ARCHITECTURE_PLAN.md
├── backend/                   # Python Flask server (PHASE 1 ✓)
│   ├── app.py                 # Main app
│   ├── config.py              # Configuration
│   ├── requirements.txt        # Dependencies
│   ├── features/              # Feature modules
│   │   ├── characters.py      # Character management
│   │   └── gameboard.py       # Map management
│   ├── data/                  # Game data (JSON files)
│   └── test_backend.py        # Test suite
├── player_web/                # Web interface (HTML/CSS/JS)
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       └── js/
└── gm_app/                    # PyQt desktop app (PHASE 3)
```

---

## Development Phases

- [x] **Phase 1: Backend Foundation** – Flask, WebSocket, Characters, Gameboard
- [ ] **Phase 2: Player Web Interface** – Browser UI, realtime updates
- [ ] **Phase 3: GM Desktop App** – PyQt app for game control
- [ ] **Phase 4: Advanced Features** – Combat, inventory, spells, NPCs
- [ ] **Phase 5: Polish & Testing** – Error handling, optimization, user testing

---

## Dependencies

- Python 3.8+
- Flask 3.0.0
- python-socketio 5.10.0
- PyQt5 (for GM app)
- Socket.IO client (JavaScript)

---

## Next Steps

1. Continue with **Phase 2: Player Web Interface**
2. Enhance WebSocket event handlers
3. Build GM desktop app (Phase 3)
4. Test with multiple clients

See [server_setup/ARCHITECTURE_PLAN.md](server_setup/ARCHITECTURE_PLAN.md) for full development roadmap.
