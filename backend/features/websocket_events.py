"""
WebSocket Event Handlers - Real-time communication handlers for all game events

Handles incoming Socket.IO events and broadcasts state changes to connected clients.
"""

import uuid
import time
from typing import Dict, Any, Optional
from flask_socketio import emit, join_room, leave_room
from features.game_state import game_state_manager, GameState
from features.characters import CharacterManager
from features.gameboard import GameboardManager


class WebSocketEventHandler:
    """Centralized WebSocket event handling"""
    
    def __init__(self, sio):
        """Initialize handlers with Socket.IO instance"""
        self.sio = sio
        self.register_handlers()
    
    def register_handlers(self):
        """Register all Socket.IO event handlers"""
        # Connection events
        self.sio.on("connect")(self.on_connect)
        self.sio.on("disconnect")(self.on_disconnect)
        self.sio.on("player_join")(self.on_player_join)
        
        # Movement events
        self.sio.on("move_character")(self.on_move_character)
        
        # Chat events
        self.sio.on("chat_message")(self.on_chat_message)
        
        # Combat events
        self.sio.on("request_combat")(self.on_request_combat)
        self.sio.on("end_combat")(self.on_end_combat)
        self.sio.on("next_turn")(self.on_next_turn)
        
        # Gameboard events
        self.sio.on("load_map")(self.on_load_map)
        self.sio.on("request_game_state")(self.on_request_game_state)
        
        # Debug/utility
        self.sio.on("echo")(self.on_echo)
    
    # ========== Connection Events ==========
    
    def on_connect(self, sid=None):
        """Handle client connection"""
        print(f"[CONNECT] Client {sid} connected")
        emit("response", {
            "status": "connected",
            "message": f"Connected to server. SID: {sid}",
            "timestamp": time.time()
        })
    
    def on_disconnect(self, sid=None):
        """Handle client disconnection"""
        print(f"[DISCONNECT] Client {sid} disconnected")
        
        # Remove player from game state
        game_state_manager.remove_player(sid)
        
        # Broadcast player left event
        self.broadcast_event("player_left", {
            "player_id": sid,
            "timestamp": time.time()
        })
    
    def on_player_join(self, data):
        """Handle player joining game with character"""
        player_id = data.get("player_id") or str(uuid.uuid4())
        character_id = data.get("character_id")
        character_name = data.get("character_name", "Unknown")
        is_gm = data.get("is_gm", False)
        
        print(f"[PLAYER_JOIN] {character_name} ({player_id}) joining as {'GM' if is_gm else 'Player'}")
        
        # Add to game state
        player = game_state_manager.add_player(
            player_id=player_id,
            character_id=character_id,
            character_name=character_name,
            is_gm=is_gm
        )
        
        # Emit confirmation to joining player
        emit("player_joined", {
            "player_id": player_id,
            "character_name": character_name,
            "timestamp": time.time()
        })
        
        # Broadcast to all others
        self.broadcast_event("player_joined", {
            "player_id": player_id,
            "character_name": character_name,
            "position": player.position,
            "timestamp": time.time()
        }, exclude=player_id)
        
        # Send current game state to new player
        self.send_current_game_state(player_id)
    
    # ========== Movement Events ==========
    
    def on_move_character(self, data):
        """Handle player character movement"""
        player_id = data.get("player_id")
        x = data.get("x")
        y = data.get("y")
        
        if player_id is None or x is None or y is None:
            emit("error", {"message": "Invalid movement data"})
            return
        
        player = game_state_manager.get_player(player_id)
        if not player:
            emit("error", {"message": "Player not found"})
            return
        
        old_pos = player.position.copy()
        
        # Validate move is within bounds
        if game_state_manager.gameboard:
            if x < 0 or y < 0 or x >= game_state_manager.gameboard.width or y >= game_state_manager.gameboard.height:
                emit("error", {"message": "Move out of bounds"})
                return
        
        # Update position
        game_state_manager.update_player_position(player_id, x, y)
        
        print(f"[MOVE] {player.character_name} moved from {old_pos} to {{'x': {x}, 'y': {y}}}")
        
        # Broadcast to all players
        self.broadcast_event("character_moved", {
            "player_id": player_id,
            "character_name": player.character_name,
            "old_position": old_pos,
            "new_position": {"x": x, "y": y},
            "timestamp": time.time()
        })
    
    # ========== Chat Events ==========
    
    def on_chat_message(self, data):
        """Handle chat message from player"""
        player_id = data.get("player_id")
        text = data.get("text", "")
        channel = data.get("channel", "party")
        
        # Sanitize input
        text = str(text)[:500]  # Max 500 chars
        
        player = game_state_manager.get_player(player_id)
        if not player:
            return
        
        print(f"[CHAT] {player.character_name}: {text}")
        
        # Broadcast to all players
        self.broadcast_event("chat_message", {
            "player_id": player_id,
            "player_name": player.character_name,
            "text": text,
            "channel": channel,
            "timestamp": time.time()
        })
    
    # ========== Combat Events ==========
    
    def on_request_combat(self, data):
        """Handle combat request from GM"""
        initiator_id = data.get("player_id")
        initiator = game_state_manager.get_player(initiator_id)
        
        # Only GM can initiate combat (for now)
        if not initiator or not initiator.is_gm:
            emit("error", {"message": "Only GM can initiate combat"})
            return
        
        participants = data.get("participants", [])
        if not participants:
            emit("error", {"message": "No participants provided"})
            return
        
        combat_id = f"combat_{uuid.uuid4().hex[:8]}"
        
        print(f"[COMBAT_START] {combat_id} with {len(participants)} participants")
        
        # Start combat in game state
        game_state_manager.start_combat(combat_id, participants)
        
        # Broadcast combat started
        self.broadcast_event("combat_initiated", {
            "combat_id": combat_id,
            "participants": participants,
            "current_turn": participants[0]["id"] if participants else None,
            "timestamp": time.time()
        })
    
    def on_end_combat(self, data):
        """Handle combat end from GM"""
        player_id = data.get("player_id")
        player = game_state_manager.get_player(player_id)
        
        if not player or not player.is_gm:
            emit("error", {"message": "Only GM can end combat"})
            return
        
        combat = game_state_manager.end_combat()
        
        if combat:
            print(f"[COMBAT_END] {combat.combat_id} ended after {combat.round_number} rounds")
            self.broadcast_event("combat_ended", {
                "combat_id": combat.combat_id,
                "total_rounds": combat.round_number,
                "timestamp": time.time()
            })
    
    def on_next_turn(self, data):
        """Handle turn advancement in combat"""
        player_id = data.get("player_id")
        player = game_state_manager.get_player(player_id)
        
        if not player or not player.is_gm:
            emit("error", {"message": "Only GM can advance turn"})
            return
        
        combat = game_state_manager.combat
        if not combat:
            emit("error", {"message": "No combat in progress"})
            return
        
        old_turn = combat.current_turn
        game_state_manager.next_turn()
        
        print(f"[TURN_ADVANCE] {old_turn} -> {combat.current_turn} (round {combat.round_number})")
        
        self.broadcast_event("turn_advanced", {
            "current_turn": combat.current_turn,
            "round": combat.round_number,
            "timestamp": time.time()
        })
    
    # ========== Gameboard Events ==========
    
    def on_load_map(self, data):
        """Handle loading a map/gameboard"""
        player_id = data.get("player_id")
        map_name = data.get("map_name")
        
        player = game_state_manager.get_player(player_id)
        if not player or not player.is_gm:
            emit("error", {"message": "Only GM can load maps"})
            return
        
        # Load gameboard from storage
        try:
            gameboard = GameboardManager.load_gameboard(map_name)
            game_state_manager.initialize_gameboard(
                map_name=map_name,
                width=gameboard.width,
                height=gameboard.height
            )
            
            print(f"[MAP_LOADED] {map_name} ({gameboard.width}x{gameboard.height})")
            
            self.broadcast_event("map_loaded", {
                "map_name": map_name,
                "width": gameboard.width,
                "height": gameboard.height,
                "timestamp": time.time()
            })
        except Exception as e:
            print(f"[ERROR] Failed to load map: {str(e)}")
            emit("error", {"message": f"Failed to load map: {str(e)}"})
    
    # ========== State Synchronization ==========
    
    def on_request_game_state(self, data):
        """Handle request for current game state"""
        player_id = data.get("player_id")
        self.send_current_game_state(player_id)
    
    def send_current_game_state(self, player_id: str):
        """Send current game state to specific player"""
        state = game_state_manager.get_public_state()
        emit("game_state_update", {
            "state": state,
            "timestamp": time.time()
        })
    
    # ========== Utility Events ==========
    
    def on_echo(self, data):
        """Echo test event (for testing/debugging)"""
        player_id = data.get("player_id")
        message = data.get("message", "")
        
        print(f"[ECHO] {player_id}: {message}")
        
        emit("echo_response", {
            "player_id": player_id,
            "message": message,
            "timestamp": time.time()
        })
    
    # ========== Broadcasting Utilities ==========
    
    def broadcast_event(self, event_name: str, data: Dict[str, Any], exclude: Optional[str] = None):
        """Broadcast event to all connected clients"""
        if exclude:
            self.sio.emit(event_name, data, skip_sid=exclude)
        else:
            self.sio.emit(event_name, data)
    
    def emit_to_player(self, player_id: str, event_name: str, data: Dict[str, Any]):
        """Emit event to specific player"""
        self.sio.emit(event_name, data, to=player_id)
    
    def get_connected_players(self):
        """Get count of connected players"""
        return len(game_state_manager.get_all_players())
    
    def get_event_stats(self) -> Dict[str, Any]:
        """Get event handler statistics"""
        return {
            "connected_players": self.get_connected_players(),
            "game_state": game_state_manager.get_public_state()
        }
