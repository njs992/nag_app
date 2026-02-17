"""Character management feature module."""

import json
import os
from config import Config

class Character:
    """Represents a player or NPC character."""
    
    def __init__(self, char_id, player_name, character_name, char_class="Fighter", level=1):
        self.id = char_id
        self.player_name = player_name
        self.character_name = character_name
        self.char_class = char_class
        self.level = level
        self.position = {"x": 0, "y": 0}
        self.health = {"current": 10, "max": 10}
        self.stats = {
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10
        }
        self.inventory = []
        self.abilities = []
    
    def to_dict(self):
        """Convert character to dictionary."""
        return {
            "id": self.id,
            "player_name": self.player_name,
            "character_name": self.character_name,
            "class": self.char_class,
            "level": self.level,
            "position": self.position,
            "health": self.health,
            "stats": self.stats,
            "inventory": self.inventory,
            "abilities": self.abilities
        }
    
    @staticmethod
    def from_dict(data):
        """Create character from dictionary."""
        char = Character(
            char_id=data.get("id"),
            player_name=data.get("player_name", ""),
            character_name=data.get("character_name", ""),
            char_class=data.get("class", "Fighter"),
            level=data.get("level", 1)
        )
        char.position = data.get("position", {"x": 0, "y": 0})
        char.health = data.get("health", {"current": 10, "max": 10})
        char.stats = data.get("stats", char.stats)
        char.inventory = data.get("inventory", [])
        char.abilities = data.get("abilities", [])
        return char


class CharacterManager:
    """Manages character creation, loading, and saving."""
    
    @staticmethod
    def save_character(character):
        """Save character to JSON file."""
        os.makedirs(Config.CHARACTERS_DIR, exist_ok=True)
        filepath = os.path.join(Config.CHARACTERS_DIR, f"{character.id}.json")
        with open(filepath, "w") as f:
            json.dump(character.to_dict(), f, indent=2)
    
    @staticmethod
    def load_character(char_id):
        """Load character from JSON file."""
        filepath = os.path.join(Config.CHARACTERS_DIR, f"{char_id}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r") as f:
            data = json.load(f)
        return Character.from_dict(data)
    
    @staticmethod
    def get_all_characters():
        """Get all saved characters."""
        characters = []
        characters_dir = Config.CHARACTERS_DIR
        if not os.path.exists(characters_dir):
            return characters
        
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                char_id = filename.replace(".json", "")
                char = CharacterManager.load_character(char_id)
                if char:
                    characters.append(char)
        
        return characters
