"""
Game State Manager - Centralized game state tracking and event dispatch

Maintains:
- Currently active game session
- Connected players and their characters
- Current map/gameboard state
- Turn order and combat state
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class GameState(Enum):
    """Current game state"""
    LOADING = "loading"
    IDLE = "idle"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    PAUSED = "paused"
    ENDED = "ended"


@dataclass
class PlayerSession:
    """Active player session"""
    player_id: str
    character_id: str
    character_name: str
    connected_at: float
    last_activity: float = field(default_factory=time.time)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0})
    is_gm: bool = False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()


@dataclass
class GameboardState:
    """Current gameboard state"""
    map_name: str
    width: int
    height: int
    tiles: Dict[str, Any] = field(default_factory=dict)
    npcs: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    fog_of_war: bool = False


@dataclass
class CombatState:
    """Active combat session"""
    combat_id: str
    participants: List[Dict[str, Any]] = field(default_factory=list)
    current_turn: Optional[str] = None
    round_number: int = 1
    started_at: float = field(default_factory=time.time)


class GameStateManager:
    """Centralized game state tracking"""
    
    def __init__(self):
        self.game_state = GameState.IDLE
        self.players: Dict[str, PlayerSession] = {}
        self.gameboard: Optional[GameboardState] = None
        self.combat: Optional[CombatState] = None
        self.message_queue: List[Dict[str, Any]] = []
        self.created_at = time.time()
    
    # ========== Player Management ==========
    
    def add_player(self, player_id: str, character_id: str, 
                   character_name: str, is_gm: bool = False) -> PlayerSession:
        """Add connected player to game"""
        player = PlayerSession(
            player_id=player_id,
            character_id=character_id,
            character_name=character_name,
            connected_at=time.time(),
            is_gm=is_gm
        )
        self.players[player_id] = player
        return player
    
    def remove_player(self, player_id: str) -> bool:
        """Remove disconnected player from game"""
        if player_id in self.players:
            del self.players[player_id]
            return True
        return False
    
    def get_player(self, player_id: str) -> Optional[PlayerSession]:
        """Get player session"""
        return self.players.get(player_id)
    
    def get_all_players(self) -> List[PlayerSession]:
        """Get all connected players"""
        return list(self.players.values())
    
    def update_player_position(self, player_id: str, x: int, y: int):
        """Update player character position"""
        if player_id in self.players:
            self.players[player_id].position = {"x": x, "y": y}
            self.players[player_id].update_activity()
    
    def get_player_position(self, player_id: str) -> Optional[Dict[str, int]]:
        """Get player character position"""
        player = self.get_player(player_id)
        return player.position if player else None
    
    # ========== Game State Management ==========
    
    def set_game_state(self, state: GameState):
        """Set overall game state"""
        self.game_state = state
    
    def get_game_state(self) -> GameState:
        """Get current game state"""
        return self.game_state
    
    # ========== Gameboard Management ==========
    
    def initialize_gameboard(self, map_name: str, width: int, height: int):
        """Initialize new gameboard"""
        self.gameboard = GameboardState(
            map_name=map_name,
            width=width,
            height=height
        )
    
    def get_gameboard(self) -> Optional[GameboardState]:
        """Get current gameboard"""
        return self.gameboard
    
    def add_gameboard_object(self, obj: Dict[str, Any]):
        """Add object to gameboard"""
        if self.gameboard:
            self.gameboard.objects.append(obj)
    
    def add_npc(self, npc: Dict[str, Any]):
        """Add NPC to gameboard"""
        if self.gameboard:
            self.gameboard.npcs.append(npc)
    
    # ========== Combat Management ==========
    
    def start_combat(self, combat_id: str, participants: List[Dict[str, Any]]):
        """Start new combat"""
        self.combat = CombatState(
            combat_id=combat_id,
            participants=participants,
            current_turn=participants[0]["id"] if participants else None
        )
        self.game_state = GameState.COMBAT
    
    def end_combat(self) -> Optional[CombatState]:
        """End current combat"""
        ended_combat = self.combat
        self.combat = None
        self.game_state = GameState.EXPLORATION
        return ended_combat
    
    def get_combat(self) -> Optional[CombatState]:
        """Get current combat"""
        return self.combat
    
    def next_turn(self):
        """Move to next participant's turn"""
        if self.combat:
            current_idx = next(
                (i for i, p in enumerate(self.combat.participants) 
                 if p["id"] == self.combat.current_turn),
                -1
            )
            if current_idx >= 0:
                next_idx = (current_idx + 1) % len(self.combat.participants)
                self.combat.current_turn = self.combat.participants[next_idx]["id"]
                
                # Increment round if wrapping around
                if next_idx == 0 and current_idx >= 0:
                    self.combat.round_number += 1
    
    # ========== Statistics ==========
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics"""
        return {
            "uptime_seconds": time.time() - self.created_at,
            "connected_players": len(self.players),
            "game_state": self.game_state.value,
            "in_combat": self.combat is not None,
            "current_map": self.gameboard.map_name if self.gameboard else None,
            "players": [
                {
                    "id": p.player_id,
                    "character": p.character_name,
                    "position": p.position,
                    "is_gm": p.is_gm
                }
                for p in self.players.values()
            ]
        }
    
    # ========== Utility ==========
    
    def reset_game(self):
        """Reset entire game state"""
        self.__init__()
    
    def get_public_state(self) -> Dict[str, Any]:
        """Get game state safe for broadcast to all clients"""
        return {
            "game_state": self.game_state.value,
            "players": [
                {
                    "id": p.player_id,
                    "character_name": p.character_name,
                    "position": p.position,
                    "character_id": p.character_id
                }
                for p in self.players.values()
            ],
            "gameboard": {
                "map_name": self.gameboard.map_name,
                "width": self.gameboard.width,
                "height": self.gameboard.height
            } if self.gameboard else None,
            "in_combat": self.combat is not None,
            "combat": {
                "combat_id": self.combat.combat_id,
                "current_turn": self.combat.current_turn,
                "round": self.combat.round_number
            } if self.combat else None
        }


# Global game state instance (one per server)
game_state_manager = GameStateManager()
