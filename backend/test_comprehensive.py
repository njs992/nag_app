"""Comprehensive test suite for Phase 1 backend."""

import os
import sys
import json
import shutil
import time
from io import StringIO

# Import application components
from config import Config
from features.characters import Character, CharacterManager
from features.gameboard import Gameboard, GameboardManager

# Test counter
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(name, status, message=""):
    """Log test result."""
    global tests_passed, tests_failed
    status_symbol = "✓" if status else "✗"
    print(f"{status_symbol} {name}")
    if message:
        print(f"  └─ {message}")
    
    test_results.append({
        "test": name,
        "status": "PASS" if status else "FAIL",
        "message": message
    })
    
    if status:
        tests_passed += 1
    else:
        tests_failed += 1

def ensure_test_directory():
    """Create test directory."""
    test_dir = os.path.join(Config.DATA_DIR, "test")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def cleanup_test_files():
    """Clean up test files."""
    test_dir = os.path.join(Config.DATA_DIR, "test")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

# ============================================================================
# SECTION 1: CONFIGURATION TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 1: CONFIGURATION TESTING")
print("=" * 70)

try:
    assert Config.HOST == "127.0.0.1", "Host configuration incorrect"
    log_test("Config: Host loaded correctly", True)
except Exception as e:
    log_test("Config: Host loaded correctly", False, str(e))

try:
    assert Config.PORT == 5000, "Port configuration incorrect"
    log_test("Config: Port loaded correctly", True)
except Exception as e:
    log_test("Config: Port loaded correctly", False, str(e))

try:
    assert Config.DEFAULT_GRID_SIZE == 50, "Grid size incorrect"
    log_test("Config: Grid size set correctly", True)
except Exception as e:
    log_test("Config: Grid size set correctly", False, str(e))

try:
    assert Config.MAX_PLAYERS_PER_GAME == 10, "Max players incorrect"
    log_test("Config: Max players set correctly", True)
except Exception as e:
    log_test("Config: Max players set correctly", False, str(e))

try:
    assert os.path.exists(Config.DATA_DIR), "Data directory doesn't exist"
    log_test("Config: Data directories exist", True, Config.DATA_DIR)
except Exception as e:
    log_test("Config: Data directories exist", False, str(e))

# ============================================================================
# SECTION 2: CHARACTER MODULE TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 2: CHARACTER MODULE TESTING")
print("=" * 70)

# Test 2.1: Character creation
try:
    char = Character("test_char_1", "TestPlayer", "TestHero", "Warrior", 3)
    assert char.id == "test_char_1"
    assert char.character_name == "TestHero"
    assert char.char_class == "Warrior"
    assert char.level == 3
    log_test("Character: Object creation works", True)
except Exception as e:
    log_test("Character: Object creation works", False, str(e))

# Test 2.2: Character to_dict
try:
    char = Character("test_char_2", "Player", "Hero", "Mage", 5)
    char_dict = char.to_dict()
    assert isinstance(char_dict, dict)
    assert "id" in char_dict
    assert "character_name" in char_dict
    assert "stats" in char_dict
    assert "inventory" in char_dict
    log_test("Character: to_dict() produces valid structure", True)
except Exception as e:
    log_test("Character: to_dict() produces valid structure", False, str(e))

# Test 2.3: Character from_dict
try:
    char_data = {
        "id": "test_char_3",
        "player_name": "Player",
        "character_name": "Loaded Hero",
        "class": "Rogue",
        "level": 4,
        "position": {"x": 5, "y": 10},
        "health": {"current": 20, "max": 30},
        "stats": {"str": 12, "dex": 15, "con": 10, "int": 8, "wis": 9, "cha": 11},
        "inventory": ["dagger", "cloak"],
        "abilities": ["backstab", "stealth"]
    }
    char = Character.from_dict(char_data)
    assert char.id == "test_char_3"
    assert char.character_name == "Loaded Hero"
    assert char.position == {"x": 5, "y": 10}
    log_test("Character: from_dict() recreates correctly", True)
except Exception as e:
    log_test("Character: from_dict() recreates correctly", False, str(e))

# Test 2.4: Character attribute updates
try:
    char = Character("test_char_4", "Player", "Hero", "Paladin", 2)
    char.position = {"x": 15, "y": 20}
    char.health = {"current": 35, "max": 35}
    char.inventory.append("holy_sword")
    
    assert char.position == {"x": 15, "y": 20}
    assert char.health["current"] == 35
    assert "holy_sword" in char.inventory
    log_test("Character: Attributes update correctly", True)
except Exception as e:
    log_test("Character: Attributes update correctly", False, str(e))

# Test 2.5: Save character
try:
    char = Character("save_test_1", "Sarah", "Elf Archer", "Ranger", 5)
    char.stats = {"str": 10, "dex": 16, "con": 12, "int": 14, "wis": 15, "cha": 13}
    CharacterManager.save_character(char)
    
    filepath = os.path.join(Config.CHARACTERS_DIR, "save_test_1.json")
    assert os.path.exists(filepath), f"File not created: {filepath}"
    log_test("Character: save_character() creates file", True, filepath)
except Exception as e:
    log_test("Character: save_character() creates file", False, str(e))

# Test 2.6: Load character
try:
    char = Character("load_test_1", "John", "Dwarf Fighter", "Fighter", 3)
    char.health = {"current": 45, "max": 50}
    CharacterManager.save_character(char)
    
    loaded = CharacterManager.load_character("load_test_1")
    assert loaded is not None, "Failed to load character"
    assert loaded.character_name == "Dwarf Fighter"
    assert loaded.health["current"] == 45
    log_test("Character: load_character() reads correctly", True)
except Exception as e:
    log_test("Character: load_character() reads correctly", False, str(e))

# Test 2.7: Get all characters
try:
    char1 = Character("multi_1", "Player1", "Hero1", "Warrior", 1)
    char2 = Character("multi_2", "Player2", "Hero2", "Mage", 2)
    CharacterManager.save_character(char1)
    CharacterManager.save_character(char2)
    
    all_chars = CharacterManager.get_all_characters()
    assert len(all_chars) >= 2, f"Expected at least 2 characters, got {len(all_chars)}"
    log_test("Character: get_all_characters() returns list", True, f"{len(all_chars)} characters")
except Exception as e:
    log_test("Character: get_all_characters() returns list", False, str(e))

# Test 2.8: Invalid character load
try:
    result = CharacterManager.load_character("nonexistent_character")
    assert result is None, "Should return None for nonexistent character"
    log_test("Character: Nonexistent load returns None", True)
except Exception as e:
    log_test("Character: Nonexistent load returns None", False, str(e))

# ============================================================================
# SECTION 3: GAMEBOARD MODULE TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 3: GAMEBOARD MODULE TESTING")
print("=" * 70)

# Test 3.1: Gameboard creation
try:
    board = Gameboard("Test Board", 15, 15)
    assert board.name == "Test Board"
    assert board.width == 15
    assert board.height == 15
    assert len(board.tiles) == 15 * 15
    log_test("Gameboard: Object creation works", True, f"{board.width}x{board.height}")
except Exception as e:
    log_test("Gameboard: Object creation works", False, str(e))

# Test 3.2: Tile initialization
try:
    board = Gameboard("Tile Test", 10, 10)
    tile_00 = board.get_tile(0, 0)
    tile_99 = board.get_tile(9, 9)
    
    assert tile_00 is not None, "Tile at (0,0) should exist"
    assert tile_99 is not None, "Tile at (9,9) should exist"
    assert tile_00.tile_type == "empty"
    log_test("Gameboard: Tiles initialize correctly", True)
except Exception as e:
    log_test("Gameboard: Tiles initialize correctly", False, str(e))

# Test 3.3: Tile modification
try:
    board = Gameboard("Modify Test", 10, 10)
    board.set_tile(5, 5, "wall", True)
    tile = board.get_tile(5, 5)
    
    assert tile.tile_type == "wall"
    assert tile.obstacle == True
    log_test("Gameboard: Tile modification works", True)
except Exception as e:
    log_test("Gameboard: Tile modification works", False, str(e))

# Test 3.4: Out of bounds tile access
try:
    board = Gameboard("Bounds Test", 10, 10)
    tile_oob = board.get_tile(15, 15)
    
    assert tile_oob is None, "Out of bounds should return None"
    log_test("Gameboard: Out-of-bounds returns None", True)
except Exception as e:
    log_test("Gameboard: Out-of-bounds returns None", False, str(e))

# Test 3.5: Gameboard to_dict
try:
    board = Gameboard("Dict Test", 8, 8)
    board.set_tile(2, 2, "grass", False)
    board_dict = board.to_dict()
    
    assert isinstance(board_dict, dict)
    assert "name" in board_dict
    assert "tiles" in board_dict
    assert len(board_dict["tiles"]) == 64
    log_test("Gameboard: to_dict() produces valid structure", True)
except Exception as e:
    log_test("Gameboard: to_dict() produces valid structure", False, str(e))

# Test 3.6: Gameboard from_dict
try:
    board_data = {
        "name": "Loaded Map",
        "width": 12,
        "height": 12,
        "tiles": [{"x": 0, "y": 0, "type": "empty", "obstacle": False, "objects": []}
                  for _ in range(144)],
        "npcs": [],
        "objects": []
    }
    board = Gameboard.from_dict(board_data)
    
    assert board.name == "Loaded Map"
    assert board.width == 12
    assert board.height == 12
    log_test("Gameboard: from_dict() recreates correctly", True)
except Exception as e:
    log_test("Gameboard: from_dict() recreates correctly", False, str(e))

# Test 3.7: Save gameboard
try:
    board = Gameboard("Save Test", 10, 10)
    board.set_tile(3, 3, "water", False)
    GameboardManager.save_gameboard(board, "test_map_1")
    
    filepath = os.path.join(Config.MAPS_DIR, "test_map_1.json")
    assert os.path.exists(filepath), f"Map file not created: {filepath}"
    log_test("Gameboard: save_gameboard() creates file", True)
except Exception as e:
    log_test("Gameboard: save_gameboard() creates file", False, str(e))

# Test 3.8: Load gameboard
try:
    board = Gameboard("Load Test", 12, 12)
    board.set_tile(4, 4, "grass", False)
    GameboardManager.save_gameboard(board, "test_map_2")
    
    loaded = GameboardManager.load_gameboard("test_map_2")
    assert loaded is not None, "Failed to load gameboard"
    assert loaded.name == "Load Test"
    assert loaded.width == 12
    log_test("Gameboard: load_gameboard() reads correctly", True)
except Exception as e:
    log_test("Gameboard: load_gameboard() reads correctly", False, str(e))

# Test 3.9: Invalid gameboard load
try:
    result = GameboardManager.load_gameboard("nonexistent_map")
    assert result is None, "Should return None for nonexistent map"
    log_test("Gameboard: Nonexistent load returns None", True)
except Exception as e:
    log_test("Gameboard: Nonexistent load returns None", False, str(e))

# ============================================================================
# SECTION 4: DATA PERSISTENCE TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 4: DATA PERSISTENCE TESTING")
print("=" * 70)

# Test 4.1: Character JSON validity
try:
    char = Character("persist_char_1", "Player", "Hero", "Warrior", 5)
    char.stats = {"str": 18, "dex": 10, "con": 16, "int": 9, "wis": 12, "cha": 11}
    CharacterManager.save_character(char)
    
    filepath = os.path.join(Config.CHARACTERS_DIR, "persist_char_1.json")
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert data["character_name"] == "Hero"
    assert data["stats"]["str"] == 18
    log_test("Data Persistence: Character JSON valid", True)
except Exception as e:
    log_test("Data Persistence: Character JSON valid", False, str(e))

# Test 4.2: Gameboard JSON validity
try:
    board = Gameboard("persist_board_1", 10, 10)
    GameboardManager.save_gameboard(board, "persist_test_1")
    
    filepath = os.path.join(Config.MAPS_DIR, "persist_test_1.json")
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, dict)
    assert data["name"] == "persist_board_1"
    assert len(data["tiles"]) == 100
    log_test("Data Persistence: Gameboard JSON valid", True)
except Exception as e:
    log_test("Data Persistence: Gameboard JSON valid", False, str(e))

# Test 4.3: Data survives multiple save/load cycles
try:
    char = Character("cycle_test", "Player", "Cycle Hero", "Paladin", 7)
    char.inventory = ["sword", "shield", "potion"]
    
    # Save and load 3 times
    for i in range(3):
        CharacterManager.save_character(char)
        char = CharacterManager.load_character("cycle_test")
    
    assert char.character_name == "Cycle Hero"
    assert "sword" in char.inventory
    log_test("Data Persistence: Multiple save/load cycles", True)
except Exception as e:
    log_test("Data Persistence: Multiple save/load cycles", False, str(e))

# Test 4.4: File overwrite works
try:
    char1 = Character("overwrite_test", "Player", "Hero V1", "Warrior", 1)
    CharacterManager.save_character(char1)
    
    char2 = Character("overwrite_test", "Player", "Hero V2", "Mage", 5)
    CharacterManager.save_character(char2)
    
    loaded = CharacterManager.load_character("overwrite_test")
    assert loaded.character_name == "Hero V2"
    assert loaded.level == 5
    log_test("Data Persistence: File overwrite works", True)
except Exception as e:
    log_test("Data Persistence: File overwrite works", False, str(e))

# ============================================================================
# SECTION 5: ERROR HANDLING TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 5: ERROR HANDLING TESTING")
print("=" * 70)

# Test 5.1: Graceful nonexistent character handling
try:
    result = CharacterManager.load_character("totally_fake_char")
    assert result is None
    log_test("Error Handling: Nonexistent character handled", True)
except Exception as e:
    log_test("Error Handling: Nonexistent character handled", False, str(e))

# Test 5.2: Graceful nonexistent map handling
try:
    result = GameboardManager.load_gameboard("totally_fake_map")
    assert result is None
    log_test("Error Handling: Nonexistent map handled", True)
except Exception as e:
    log_test("Error Handling: Nonexistent map handled", False, str(e))

# Test 5.3: Empty character list when no files
try:
    chars = CharacterManager.get_all_characters()
    assert isinstance(chars, list)
    log_test("Error Handling: Empty character list returns list", True)
except Exception as e:
    log_test("Error Handling: Empty character list returns list", False, str(e))

# Test 5.4: Invalid tile coordinates
try:
    board = Gameboard("Error Test", 10, 10)
    tile = board.get_tile(-1, -1)
    assert tile is None
    log_test("Error Handling: Negative tile coordinates", True)
except Exception as e:
    log_test("Error Handling: Negative tile coordinates", False, str(e))

# Test 5.5: Large tile coordinates
try:
    board = Gameboard("Error Test 2", 10, 10)
    tile = board.get_tile(1000, 1000)
    assert tile is None
    log_test("Error Handling: Large tile coordinates", True)
except Exception as e:
    log_test("Error Handling: Large tile coordinates", False, str(e))

# ============================================================================
# SECTION 6: INTEGRATION TESTING
# ============================================================================

print("\n" + "=" * 70)
print("SECTION 6: INTEGRATION TESTING")
print("=" * 70)

# Test 6.1: Create character, save, load, modify, save again
try:
    char = Character("integration_1", "Alice", "Alice's Hero", "Rogue", 4)
    char.inventory = ["lockpick", "dagger"]
    CharacterManager.save_character(char)
    
    loaded1 = CharacterManager.load_character("integration_1")
    loaded1.level = 5
    loaded1.inventory.append("boots")
    CharacterManager.save_character(loaded1)
    
    loaded2 = CharacterManager.load_character("integration_1")
    assert loaded2.level == 5
    assert "boots" in loaded2.inventory
    log_test("Integration: Character full lifecycle", True)
except Exception as e:
    log_test("Integration: Character full lifecycle", False, str(e))

# Test 6.2: Create map, modify, save, load, modify, save
try:
    board = Gameboard("integration_map_1", 15, 15)
    board.set_tile(5, 5, "grass", False)
    board.set_tile(10, 10, "wall", True)
    GameboardManager.save_gameboard(board, "integration_map_1")
    
    loaded1 = GameboardManager.load_gameboard("integration_map_1")
    loaded1.set_tile(7, 7, "water", False)
    GameboardManager.save_gameboard(loaded1, "integration_map_1")
    
    loaded2 = GameboardManager.load_gameboard("integration_map_1")
    water_tile = loaded2.get_tile(7, 7)
    assert water_tile.tile_type == "water"
    log_test("Integration: Gameboard full lifecycle", True)
except Exception as e:
    log_test("Integration: Gameboard full lifecycle", False, str(e))

# Test 6.3: Multiple characters and boards coexist
try:
    for i in range(5):
        char = Character(f"multi_char_{i}", f"Player{i}", f"Hero{i}", "Warrior", i+1)
        CharacterManager.save_character(char)
    
    for i in range(3):
        board = Gameboard(f"multi_board_{i}", 10, 10)
        GameboardManager.save_gameboard(board, f"multi_board_{i}")
    
    chars = CharacterManager.get_all_characters()
    assert len(chars) >= 5
    log_test("Integration: Multiple entities coexist", True, f"{len(chars)} characters")
except Exception as e:
    log_test("Integration: Multiple entities coexist", False, str(e))

# ============================================================================
# FINAL REPORT
# ============================================================================

print("\n" + "=" * 70)
print("TEST EXECUTION COMPLETE")
print("=" * 70)

print(f"\nTests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests: {tests_passed + tests_failed}")

if tests_failed == 0:
    print("\n✓ ALL TESTS PASSED!")
    print("\nPhase 1 Backend is ready for deployment.")
else:
    print(f"\n✗ {tests_failed} TEST(S) FAILED")
    print("\nFailed tests:")
    for result in test_results:
        if result["status"] == "FAIL":
            print(f"  - {result['test']}: {result['message']}")

# Save results to file
with open("test_results.txt", "w") as f:
    f.write("=" * 70 + "\n")
    f.write("PHASE 1 COMPREHENSIVE TEST RESULTS\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Tests Passed: {tests_passed}\n")
    f.write(f"Tests Failed: {tests_failed}\n")
    f.write(f"Total Tests: {tests_passed + tests_failed}\n")
    f.write(f"Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%\n\n")
    f.write("Detailed Results:\n")
    f.write("-" * 70 + "\n")
    for result in test_results:
        f.write(f"[{result['status']}] {result['test']}\n")
        if result['message']:
            f.write(f"      {result['message']}\n")

print("\nTest results saved to: test_results.txt")

# Exit with appropriate code
sys.exit(0 if tests_failed == 0 else 1)
