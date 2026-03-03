#!/usr/bin/env python3
"""
Quick WebSocket Events Test

Tests the WebSocket event system with running server.
"""

import socketio
import time
import json

SERVER_URL = "http://localhost:5000"

def test_basic_connection():
    """Test basic Socket.IO connection"""
    print("\n" + "="*60)
    print("Test 1: Basic Connection")
    print("="*60)
    
    sio = socketio.Client()
    
    try:
        sio.connect(SERVER_URL, transports=['polling'])
        print("✓ Connected to server")
        time.sleep(0.5)
        sio.disconnect()
        print("✓ Disconnected successfully")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False


def test_player_join():
    """Test player join event"""
    print("\n" + "="*60)
    print("Test 2: Player Join Event")
    print("="*60)
    
    received_events = []
    
    sio = socketio.Client()
    
    @sio.on('*')
    def on_event(event, data):
        received_events.append({'event': event, 'data': data})
    
    try:
        sio.connect(SERVER_URL, transports=['polling'])
        print("✓ Connected")
        
        # Join game
        sio.emit('player_join', {
            'player_id': 'test_player_1',
            'character_id': 'test_char_1',
            'character_name': 'TestCharacter',
            'is_gm': False
        })
        print("✓ Emitted player_join")
        
        # Wait for response
        time.sleep(1)
        
        # Check for player_joined event
        player_joined_events = [e for e in received_events if e['event'] == 'player_joined']
        if player_joined_events:
            data = player_joined_events[0]['data']
            print(f"✓ Received player_joined: {data['character_name']}")
            return True
        else:
            print(f"✗ No player_joined event received")
            print(f"  Received events: {[e['event'] for e in received_events]}")
            return False
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        sio.disconnect()


def test_movement():
    """Test character movement event"""
    print("\n" + "="*60)
    print("Test 3: Character Movement")
    print("="*60)
    
    # Player 1
    client1_events = []
    sio1 = socketio.Client()
    
    @sio1.on('*')
    def on_event1(event, data):
        client1_events.append({'event': event, 'data': data})
    
    # Player 2
    client2_events = []
    sio2 = socketio.Client()
    
    @sio2.on('*')
    def on_event2(event, data):
        client2_events.append({'event': event, 'data': data})
    
    try:
        # Connect both
        sio1.connect(SERVER_URL, transports=['polling'])
        sio2.connect(SERVER_URL, transports=['polling'])
        print("✓ Both clients connected")
        time.sleep(0.3)
        
        # Both join
        sio1.emit('player_join', {
            'player_id': 'move_player_1',
            'character_id': 'move_char_1',
            'character_name': 'Mover1',
            'is_gm': False
        })
        
        sio2.emit('player_join', {
            'player_id': 'move_player_2',
            'character_id': 'move_char_2',
            'character_name': 'Observer2',
            'is_gm': False
        })
        print("✓ Both players joined")
        time.sleep(0.5)
        
        # Player 1 moves
        sio1.emit('move_character', {
            'player_id': 'move_player_1',
            'x': 15,
            'y': 20
        })
        print("✓ Player 1 moved")
        time.sleep(0.5)
        
        # Check if Player 2 received movement event
        movement_events = [e for e in client2_events if e['event'] == 'character_moved']
        if movement_events:
            data = movement_events[0]['data']
            print(f"✓ Player 2 received movement: {data['character_name']} → ({data['new_position']['x']}, {data['new_position']['y']})")
            return True
        else:
            print(f"✗ Movement not broadcast to other player")
            print(f"  Client1 events: {[e['event'] for e in client1_events]}")
            print(f"  Client2 events: {[e['event'] for e in client2_events]}")
            return False
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        sio1.disconnect()
        sio2.disconnect()


def test_chat():
    """Test chat message broadcasting"""
    print("\n" + "="*60)
    print("Test 4: Chat Message Broadcasting")
    print("="*60)
    
    client1_events = []
    sio1 = socketio.Client()
    
    @sio1.on('*')
    def on_event1(event, data):
        client1_events.append({'event': event, 'data': data})
    
    client2_events = []
    sio2 = socketio.Client()
    
    @sio2.on('*')
    def on_event2(event, data):
        client2_events.append({'event': event, 'data': data})
    
    try:
        # Connect and join
        sio1.connect(SERVER_URL, transports=['polling'])
        sio2.connect(SERVER_URL, transports=['polling'])
        time.sleep(0.3)
        
        sio1.emit('player_join', {
            'player_id': 'chat_p1',
            'character_id': 'chat_c1',
            'character_name': 'ChatPlayer1',
            'is_gm': False
        })
        
        sio2.emit('player_join', {
            'player_id': 'chat_p2',
            'character_id': 'chat_c2',
            'character_name': 'ChatPlayer2',
            'is_gm': False
        })
        print("✓ Both players joined")
        time.sleep(0.5)
        
        # Send chat
        sio1.emit('chat_message', {
            'player_id': 'chat_p1',
            'text': 'Hello everyone!',
            'channel': 'party'
        })
        print("✓ Player 1 sent chat")
        time.sleep(0.5)
        
        # Check if Player 2 received message
        chat_events = [e for e in client2_events if e['event'] == 'chat_message']
        if chat_events:
            data = chat_events[0]['data']
            print(f"✓ Player 2 received: [{data['player_name']}]: {data['text']}")
            return True
        else:
            print(f"✗ Chat not broadcast")
            return False
    
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    finally:
        sio1.disconnect()
        sio2.disconnect()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WEBSOCKET EVENT SYSTEM QUICK TEST")
    print("="*60)
    print(f"Server: {SERVER_URL}")
    
    results = {
        'Connection': test_basic_connection(),
        'Player Join': test_player_join(),
        'Movement': test_movement(),
        'Chat': test_chat(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! WebSocket event system is working.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
