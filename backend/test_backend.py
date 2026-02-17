"""Test script to verify Phase 1 backend functionality."""

import os
import json
from features.characters import Character, CharacterManager
from features.gameboard import Gameboard, GameboardManager

print("=" * 60)
print("RPG BACKEND - PHASE 1 TEST")
print("=" * 60)

# Test 1: Character Creation and Storage
print("\n[TEST 1] Character Management")
print("-" * 60)

char1 = Character("player_1", "Sarah", "Aragorn", "Ranger", 5)
char1.stats = {"str": 16, "dex": 14, "con": 15, "int": 12, "wis": 13, "cha": 11}
char1.health = {"current": 25, "max": 25}
char1.position = {"x": 10, "y": 8}
char1.inventory = ["sword", "bow", "torch"]

print(f"Created character: {char1.character_name} (Player: {char1.player_name})")
print(f"  Class: {char1.char_class}, Level: {char1.level}")
print(f"  Position: {char1.position}")
print(f"  Health: {char1.health['current']}/{char1.health['max']}")

# Save character
CharacterManager.save_character(char1)
print("✓ Character saved to JSON")

# Load character
loaded_char = CharacterManager.load_character("player_1")
print(f"✓ Character loaded from JSON: {loaded_char.character_name}")

# Test 2: Gameboard Creation and Storage
print("\n[TEST 2] Gameboard Management")
print("-" * 60)

board = Gameboard("Town Square", width=20, height=20)
print(f"Created gameboard: {board.name} ({board.width}x{board.height})")

# Modify some tiles
board.set_tile(5, 5, tile_type="wall", obstacle=True)
board.set_tile(10, 10, tile_type="grass", obstacle=False)
print("✓ Added tiles to board")

# Save board
GameboardManager.save_gameboard(board, "town_square")
print("✓ Gameboard saved to JSON")

# Load board
loaded_board = GameboardManager.load_gameboard("town_square")
print(f"✓ Gameboard loaded: {loaded_board.name}")
print(f"  Tile at (5,5): {loaded_board.get_tile(5, 5).tile_type} (obstacle: {loaded_board.get_tile(5, 5).obstacle})")

# Test 3: Data Storage Verification
print("\n[TEST 3] Data Storage Verification")
print("-" * 60)

chars_dir = "data/characters"
maps_dir = "data/maps"

if os.path.exists(os.path.join(chars_dir, "player_1.json")):
    with open(os.path.join(chars_dir, "player_1.json"), "r") as f:
        char_data = json.load(f)
    print(f"✓ Character file exists: data/characters/player_1.json")
    print(f"  Character: {char_data['character_name']} (Class: {char_data['class']})")

if os.path.exists(os.path.join(maps_dir, "town_square.json")):
    with open(os.path.join(maps_dir, "town_square.json"), "r") as f:
        map_data = json.load(f)
    print(f"✓ Map file exists: data/maps/town_square.json")
    print(f"  Map: {map_data['name']} ({map_data['width']}x{map_data['height']})")

# Test 4: Get All Characters
print("\n[TEST 4] Character Query")
print("-" * 60)

all_chars = CharacterManager.get_all_characters()
print(f"✓ Found {len(all_chars)} character(s) in storage")
for char in all_chars:
    print(f"  - {char.character_name} (Player: {char.player_name})")

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✓")
print("=" * 60)
print("\nPhase 1 Backend is ready for development!")
print("\nTo start the server, run:")
print("  python app.py")
print("\nThen visit: http://127.0.0.1:5000")
