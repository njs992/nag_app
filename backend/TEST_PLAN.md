# Phase 1 Test Plan - Backend Foundation

## Overview

This test plan ensures all Phase 1 components are functioning correctly before moving to Phase 2. Tests cover configuration, API endpoints, WebSocket, feature modules, and data persistence.

---

## Test Categories

### 1. Configuration Testing
- [ ] Configuration loads from environment
- [ ] Config defaults work when no .env file exists
- [ ] Data directories are created on startup
- [ ] Server configuration accessible via `/api/config`

### 2. API Endpoint Testing
- [ ] `GET /` returns HTML (player interface)
- [ ] `GET /api/health` returns status 200
- [ ] `GET /api/config` returns server config
- [ ] Invalid endpoints return 404
- [ ] Server error handling works (500 errors)

### 3. WebSocket Connection Testing
- [ ] Client can connect to WebSocket
- [ ] Connection event fires on client connect
- [ ] Disconnect event fires on client disconnect
- [ ] Echo test works (server echoes messages back)
- [ ] Multiple clients can connect simultaneously
- [ ] WebSocket events are properly formatted

### 4. Character Module Testing
- [ ] Character object creation works
- [ ] Character.to_dict() produces valid JSON structure
- [ ] Character.from_dict() recreates character correctly
- [ ] CharacterManager.save_character() creates JSON file
- [ ] CharacterManager.load_character() reads JSON correctly
- [ ] CharacterManager.get_all_characters() returns list
- [ ] Character data persists across save/load cycles
- [ ] Invalid character IDs handled gracefully
- [ ] Character attributes update correctly

### 5. Gameboard Module Testing
- [ ] Gameboard object creation works
- [ ] Tiles initialize correctly
- [ ] GameboardTile.to_dict() produces valid structure
- [ ] Gameboard.to_dict() includes all data
- [ ] Gameboard.from_dict() recreates board correctly
- [ ] Tile modification works (set_tile method)
- [ ] GameboardManager.save_gameboard() creates JSON
- [ ] GameboardManager.load_gameboard() reads correctly
- [ ] get_all_characters() returns empty list gracefully
- [ ] Map data persists across save/load cycles

### 6. Data Persistence Testing
- [ ] Character JSON files have correct format
- [ ] Map JSON files have correct format
- [ ] JSON files are readable and valid
- [ ] Data survives across multiple save/load cycles
- [ ] Directory structure created automatically
- [ ] Existing files can be overwritten

### 7. Error Handling Testing
- [ ] Loading non-existent character returns None
- [ ] Loading non-existent map returns None
- [ ] Invalid JSON doesn't crash system
- [ ] Out-of-bounds tile access returns None
- [ ] Missing required fields handled gracefully
- [ ] File permission errors handled

### 8. Integration Testing
- [ ] Create characters and save them
- [ ] Load characters and verify data
- [ ] Create maps and save them
- [ ] Load maps and verify data
- [ ] Modify and re-save characters
- [ ] Modify and re-save maps
- [ ] Clean up test files

---

## Test Execution

Run all tests with:
```bash
python test_comprehensive.py
```

Test results and coverage report will be generated.

---

## Success Criteria

✓ **All 8 test categories pass**  
✓ **100% of critical functionality verified**  
✓ **No unhandled exceptions**  
✓ **Data integrity maintained**  
✓ **Performance acceptable (<100ms for operations)**  

---

## Test Coverage Matrix

| Component | Unit Tests | Integration Tests | System Tests |
|-----------|------------|-------------------|--------------|
| Configuration | ✓ | ✓ | ✓ |
| API Endpoints | ✓ | ✓ | ✓ |
| WebSocket | ✓ | ✓ | ✓ |
| Characters | ✓ | ✓ | ✓ |
| Gameboard | ✓ | ✓ | ✓ |
| File I/O | ✓ | ✓ | ✓ |
| Error Handling | ✓ | ✓ | ✓ |

---

## Notes

- All tests are automated and reproducible
- Tests create temporary test files in `data/test/` directory
- Tests clean up after themselves
- WebSocket tests may require manual verification of connection
- Test results logged to `test_results.log`

---

## After Testing

Once all tests pass:
1. Commit changes to GitHub
2. Move to Phase 2: Player Web Interface
3. Begin building advanced features
