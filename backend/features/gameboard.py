"""Gameboard and map management feature module."""

import json
import os
from config import Config

class GameboardTile:
    """Represents a single tile on the gameboard."""
    
    def __init__(self, x, y, tile_type="empty", obstacle=False):
        self.x = x
        self.y = y
        self.tile_type = tile_type  # "empty", "wall", "water", "grass", etc.
        self.obstacle = obstacle
        self.objects = []  # NPCs, items, etc. on this tile
    
    def to_dict(self):
        """Convert tile to dictionary."""
        return {
            "x": self.x,
            "y": self.y,
            "type": self.tile_type,
            "obstacle": self.obstacle,
            "objects": self.objects
        }


class Gameboard:
    """Represents the game map/board."""
    
    def __init__(self, name, width=20, height=20):
        self.name = name
        self.width = width
        self.height = height
        self.tiles = self._initialize_tiles()
        self.npcs = []
        self.objects = []
    
    def _initialize_tiles(self):
        """Create a grid of empty tiles."""
        tiles = {}
        for x in range(self.width):
            for y in range(self.height):
                tiles[(x, y)] = GameboardTile(x, y)
        return tiles
    
    def get_tile(self, x, y):
        """Get tile at coordinates."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[(x, y)]
        return None
    
    def set_tile(self, x, y, tile_type="empty", obstacle=False):
        """Modify a tile."""
        tile = self.get_tile(x, y)
        if tile:
            tile.tile_type = tile_type
            tile.obstacle = obstacle
    
    def to_dict(self):
        """Convert gameboard to dictionary."""
        tiles_list = [tile.to_dict() for tile in self.tiles.values()]
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "tiles": tiles_list,
            "npcs": self.npcs,
            "objects": self.objects
        }
    
    @staticmethod
    def from_dict(data):
        """Create gameboard from dictionary."""
        board = Gameboard(
            name=data.get("name", "Untitled Map"),
            width=data.get("width", 20),
            height=data.get("height", 20)
        )
        # Restore tiles
        for tile_data in data.get("tiles", []):
            board.set_tile(
                tile_data["x"],
                tile_data["y"],
                tile_data.get("type", "empty"),
                tile_data.get("obstacle", False)
            )
        board.npcs = data.get("npcs", [])
        board.objects = data.get("objects", [])
        return board


class GameboardManager:
    """Manages map creation, loading, and saving."""
    
    @staticmethod
    def save_gameboard(gameboard, map_name=None):
        """Save gameboard to JSON file."""
        os.makedirs(Config.MAPS_DIR, exist_ok=True)
        name = map_name or gameboard.name
        filepath = os.path.join(Config.MAPS_DIR, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump(gameboard.to_dict(), f, indent=2)
    
    @staticmethod
    def load_gameboard(map_name):
        """Load gameboard from JSON file."""
        filepath = os.path.join(Config.MAPS_DIR, f"{map_name}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return Gameboard.from_dict(data)
    
    @staticmethod
    def create_default_map(name="default_map"):
        """Create a basic default map."""
        board = Gameboard(name, width=20, height=20)
        return board
