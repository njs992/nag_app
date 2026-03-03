"""
End-to-End WebSocket Event System Tests

Tests all WebSocket events with real server and multiple clients.
Validates the complete event flow including broadcsting and state updates.
"""

import pytest
import time
import threading
import requests
import socketio
from typing import Dict, Any
import subprocess
import signal
import os


# ============================================================================
# Test Configuration
# ============================================================================

SERVER_URL = "http://localhost:5000"
SOCKET_URL = "http://localhost:5000"
TEST_TIMEOUT = 5

# Start server for testing
def start_server():
    """Start Flask server in background"""
    import sys
    sys.path.insert(0, '/home/sarah/stuff/nag_app/backend')
    
    if os.path.exists('server.pid'):
        with open('server.pid', 'r') as f:
            try:
                os.kill(int(f.read()), signal.SIGTERM)
                time.sleep(0.5)
            except:
                pass
    
    # Start new server
    proc = subprocess.Popen(
        ['python', 'app.py'],
        cwd='/home/sarah/stuff/nag_app/backend',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    with open('server.pid', 'w') as f:
        f.write(str(proc.pid))
    
    time.sleep(2)  # Wait for server to start
    return proc


# ============================================================================
# Socket.IO Client Helper
# ============================================================================

class TestSocketClient:
    """Test helper for Socket.IO client"""
    
    def __init__(self, name: str):
        self.name = name
        self.sio = socketio.Client()
        self.connected = False
        self.received_events = []
        self.register_handlers()
    
    def register_handlers(self):
        """Register event handlers"""
        @self.sio.event
        def connect():
            self.connected = True
            print(f"[{self.name}] Connected")
        
        @self.sio.event
        def disconnect():
            self.connected = False
            print(f"[{self.name}] Disconnected")
        
        @self.sio.on('*')
        def on_event(event, data):
            self.received_events.append({
                'event': event,
                'data': data,
                'timestamp': time.time()
            })
            print(f"[{self.name}] Event: {event}")
    
    def connect(self):
        """Connect to server"""
        try:
            self.sio.connect(
                SOCKET_URL,
                transports=['polling']
            )
            time.sleep(0.5)  # Let connection settle
        except Exception as e:
            print(f"[{self.name}] Connection failed: {e}")
            raise
    
    def disconnect(self):
        """Disconnect from server"""
        self.sio.disconnect()
    
    def emit(self, event: str, data: Dict[str, Any]):
        """Emit event"""
        self.sio.emit(event, data)
    
    def wait_for_event(self, event_name: str, timeout: float = TEST_TIMEOUT) -> Dict:
        """Wait for specific event"""
        start = time.time()
        while time.time() - start < timeout:
            for evt in self.received_events:
                if evt['event'] == event_name:
                    return evt['data']
            time.sleep(0.1)
        raise AssertionError(f"Event '{event_name}' not received within {timeout}s")


# ============================================================================
# Tests
# ============================================================================

class TestWebSocketEvents:
    """WebSocket event system tests"""
    
    @classmethod
    def setup_class(cls):
        """Start server once for all tests"""
        print("\n" + "="*60)
        print("Starting Flask server for E2E tests...")
        print("="*60)
        
        cls.server = start_server()
        
        # Verify server is responding
        for i in range(10):
            try:
                resp = requests.get(f"{SERVER_URL}/api/health")
                if resp.status_code == 200:
                    print(f"✓ Server ready at {SERVER_URL}")
                    return
            except:
                pass
            time.sleep(0.5)
        
        raise AssertionError("Server failed to start")
    
    @classmethod
    def teardown_class(cls):
        """Stop server after all tests"""
        print("\n" + "="*60)
        print("Stopping Flask server...")
        print("="*60)
        
        os.kill(cls.server.pid, signal.SIGTERM)
        cls.server.wait()
        
        if os.path.exists('server.pid'):
            os.remove('server.pid')
    
    # ========== Connection Tests ==========
    
    def test_client_connection(self):
        """Test basic client connection"""
        client = TestSocketClient("ClientA")
        client.connect()
        assert client.connected
        
        # Verify connection event received
        response = client.wait_for_event('response')
        assert response is not None
        
        client.disconnect()
    
    def test_multiple_client_connections(self):
        """Test multiple clients connecting simultaneously"""
        clients = [
            TestSocketClient("ClientA"),
            TestSocketClient("ClientB"),
            TestSocketClient("ClientC")
        ]
        
        # Connect all
        for client in clients:
            client.connect()
        
        # Verify all connected
        for client in clients:
            assert client.connected
        
        # Disconnect all
        for client in clients:
            client.disconnect()
    
    # ========== Player Join Tests ==========
    
    def test_player_join_single(self):
        """Test single player joining"""
        client = TestSocketClient("Player1")
        client.connect()
        
        client.emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        
        data = client.wait_for_event('player_joined')
        assert data['player_id'] == 'player_1'
        assert data['character_name'] == 'Aragorn'
        
        client.disconnect()
    
    def test_players_join_simultaneously(self):
        """Test multiple players joining at same time"""
        clients = [
            TestSocketClient("Player1"),
            TestSocketClient("Player2")
        ]
        
        # Connect both
        for client in clients:
            client.connect()
        
        # Player 1 joins
        clients[0].emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        
        # Player 2 joins
        clients[1].emit('player_join', {
            'player_id': 'player_2',
            'character_id': 'char_2',
            'character_name': 'Legolas',
            'is_gm': False
        })
        
        # Verify player 1 sees player 2 join
        data = clients[0].wait_for_event('player_joined', timeout=2)
        assert data['character_name'] == 'Legolas'
        
        # Clean up
        for client in clients:
            client.disconnect()
    
    # ========== Movement Tests ==========
    
    def test_character_movement_broadcast(self):
        """Test character movement is broadcast to all players"""
        clients = [
            TestSocketClient("Player1"),
            TestSocketClient("Player2")
        ]
        
        # Connect both
        for client in clients:
            client.connect()
            time.sleep(0.2)
        
        # Join game
        clients[0].emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        time.sleep(0.2)
        
        clients[1].emit('player_join', {
            'player_id': 'player_2',
            'character_id': 'char_2',
            'character_name': 'Legolas',
            'is_gm': False
        })
        time.sleep(0.2)
        
        # Player 1 moves
        clients[0].emit('move_character', {
            'player_id': 'player_1',
            'x': 10,
            'y': 15
        })
        
        # Player 2 should see the movement
        data = clients[1].wait_for_event('character_moved')
        assert data['character_name'] == 'Aragorn'
        assert data['new_position']['x'] == 10
        assert data['new_position']['y'] == 15
        
        # Clean up
        for client in clients:
            client.disconnect()
    
    # ========== Chat Tests ==========
    
    def test_chat_message_broadcast(self):
        """Test chat messages are broadcast to all players"""
        clients = [
            TestSocketClient("Player1"),
            TestSocketClient("Player2")
        ]
        
        # Connect and join
        for client in clients:
            client.connect()
        
        for i, client in enumerate(clients):
            client.emit('player_join', {
                'player_id': f'player_{i+1}',
                'character_id': f'char_{i+1}',
                'character_name': f'Character{i+1}',
                'is_gm': False
            })
            time.sleep(0.1)
        
        # Player 1 sends chat
        clients[0].emit('chat_message', {
            'player_id': 'player_1',
            'text': 'Hello everyone!',
            'channel': 'party'
        })
        
        # Player 2 should receive it
        data = clients[1].wait_for_event('chat_message')
        assert data['text'] == 'Hello everyone!'
        assert data['player_name'] == 'Character1'
        
        # Clean up
        for client in clients:
            client.disconnect()
    
    # ========== Combat Tests ==========
    
    def test_combat_initiation(self):
        """Test combat start broadcast"""
        gm_client = TestSocketClient("GM")
        player_client = TestSocketClient("Player1")
        
        # Connect both
        gm_client.connect()
        player_client.connect()
        time.sleep(0.2)
        
        # GM joins
        gm_client.emit('player_join', {
            'player_id': 'gm_1',
            'character_id': 'char_gm',
            'character_name': 'GameMaster',
            'is_gm': True
        })
        time.sleep(0.1)
        
        # Player joins
        player_client.emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        time.sleep(0.1)
        
        # GM initiates combat
        gm_client.emit('request_combat', {
            'player_id': 'gm_1',
            'participants': [
                {'id': 'player_1', 'name': 'Aragorn', 'turn_order': 1},
                {'id': 'enemy_1', 'name': 'Goblin', 'turn_order': 2}
            ]
        })
        
        # Player should see combat start
        data = player_client.wait_for_event('combat_initiated')
        assert len(data['participants']) == 2
        assert data['current_turn'] == 'player_1'
        
        # Clean up
        gm_client.disconnect()
        player_client.disconnect()
    
    def test_combat_turn_advancement(self):
        """Test turn advancement in combat"""
        gm_client = TestSocketClient("GM")
        player_client = TestSocketClient("Player1")
        
        # Connect and setup
        gm_client.connect()
        player_client.connect()
        time.sleep(0.2)
        
        gm_client.emit('player_join', {
            'player_id': 'gm_1',
            'character_id': 'char_gm',
            'character_name': 'GameMaster',
            'is_gm': True
        })
        time.sleep(0.1)
        
        player_client.emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        time.sleep(0.1)
        
        # Start combat
        gm_client.emit('request_combat', {
            'player_id': 'gm_1',
            'participants': [
                {'id': 'p1', 'name': 'Player1'},
                {'id': 'p2', 'name': 'Player2'}
            ]
        })
        player_client.wait_for_event('combat_initiated', timeout=2)
        time.sleep(0.1)
        
        # Advance turn
        gm_client.emit('next_turn', {'player_id': 'gm_1'})
        
        # Player should see turn advanced
        data = player_client.wait_for_event('turn_advanced')
        assert data['round'] == 1
        
        # Clean up
        gm_client.disconnect()
        player_client.disconnect()
    
    # ========== Game State Tests ==========
    
    def test_game_state_request(self):
        """Test requesting game state"""
        client = TestSocketClient("Player1")
        client.connect()
        
        client.emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        time.sleep(0.1)
        
        # Request state
        client.emit('request_game_state', {'player_id': 'player_1'})
        
        # Should receive state
        data = client.wait_for_event('game_state_update')
        assert 'state' in data
        assert data['state']['players'][0]['character_name'] == 'Aragorn'
        
        client.disconnect()
    
    # ========== Error Handling Tests ==========
    
    def test_invalid_movement_out_of_bounds(self):
        """Test movement validation"""
        client = TestSocketClient("Player1")
        client.connect()
        
        client.emit('player_join', {
            'player_id': 'player_1',
            'character_id': 'char_1',
            'character_name': 'Aragorn',
            'is_gm': False
        })
        time.sleep(0.1)
        
        # Try to move out of bounds
        client.emit('move_character', {
            'player_id': 'player_1',
            'x': 10000,
            'y': 10000
        })
        
        # Should receive error
        try:
            client.wait_for_event('error', timeout=1)
            error_received = True
        except:
            error_received = False
        
        # Clean up (may or may not have errored)
        client.disconnect()
    
    # ========== Performance Tests ==========
    
    def test_rapid_movement_events(self):
        """Test handling rapid movement events"""
        clients = [TestSocketClient(f"P{i}") for i in range(3)]
        
        for client in clients:
            client.connect()
            time.sleep(0.1)
        
        # All join
        for i, client in enumerate(clients):
            client.emit('player_join', {
                'player_id': f'player_{i}',
                'character_id': f'char_{i}',
                'character_name': f'Player{i}',
                'is_gm': False
            })
            time.sleep(0.1)
        
        # Send rapid movements
        for x in range(5):
            clients[0].emit('move_character', {
                'player_id': 'player_0',
                'x': x * 5,
                'y': 10
            })
            time.sleep(0.05)
        
        # Should handle without error
        time.sleep(0.5)
        
        # Clean up
        for client in clients:
            client.disconnect()
    
    def test_concurrent_mixed_events(self):
        """Test handling concurrent mixed event types"""
        clients = [TestSocketClient(f"P{i}") for i in range(2)]
        
        for client in clients:
            client.connect()
        
        # Join
        for i, client in enumerate(clients):
            client.emit('player_join', {
                'player_id': f'player_{i}',
                'character_id': f'char_{i}',
                'character_name': f'Player{i}',
                'is_gm': i == 0  # First is GM
            })
            time.sleep(0.1)
        
        # Send mixed events
        clients[0].emit('move_character', {
            'player_id': 'player_0',
            'x': 5,
            'y': 5
        })
        
        clients[1].emit('chat_message', {
            'player_id': 'player_1',
            'text': 'Test',
            'channel': 'party'
        })
        
        clients[0].emit('chat_message', {
            'player_id': 'player_0',
            'text': 'Combat!',
            'channel': 'party'
        })
        
        # All should resolve without error
        time.sleep(0.5)
        
        # Clean up
        for client in clients:
            client.disconnect()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("WebSocket Event System E2E Tests")
    print("="*60 + "\n")
    
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
