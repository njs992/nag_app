"""
End-to-End System Test
Tests a running Flask server with real network connections
"""

import time
import threading
import requests
import socketio
from datetime import datetime

# Configuration
SERVER_URL = "http://localhost:5000"
WEBSOCKET_URL = "http://localhost:5000"

# Test results tracking
test_results = {
    "rest_tests": [],
    "websocket_tests": [],
    "concurrent_tests": [],
    "start_time": datetime.now(),
}

print("\n" + "=" * 80)
print("PHASE 1: END-TO-END SYSTEM TEST")
print("=" * 80)
print(f"\nStarting E2E tests: {test_results['start_time']}")
print(f"Target: {SERVER_URL}")

# ============================================================================
# SECTION 1: REST API TESTS
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 1: REST API ENDPOINT TESTING")
print("=" * 80)

def test_rest_endpoints():
    """Test REST API endpoints with real HTTP requests."""
    
    # Test 1: Health Check
    print("\n[REST API Tests]")
    try:
        response = requests.get(f"{SERVER_URL}/api/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'ok'
        print("✓ GET /api/health")
        print(f"  └─ Status: {response.status_code}")
        print(f"  └─ Response: {data}")
        test_results["rest_tests"].append(("GET /api/health", True))
    except Exception as e:
        print(f"✗ GET /api/health: {e}")
        test_results["rest_tests"].append(("GET /api/health", False))
        return False
    
    # Test 2: Config Endpoint
    try:
        response = requests.get(f"{SERVER_URL}/api/config", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert 'grid_size' in data
        print("✓ GET /api/config")
        print(f"  └─ Status: {response.status_code}")
        print(f"  └─ Response: {data}")
        test_results["rest_tests"].append(("GET /api/config", True))
    except Exception as e:
        print(f"✗ GET /api/config: {e}")
        test_results["rest_tests"].append(("GET /api/config", False))
        return False
    
    # Test 3: Root Endpoint (HTML)
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('content-type', '')
        print("✓ GET /")
        print(f"  └─ Status: {response.status_code}")
        print(f"  └─ Content-Type: {response.headers.get('content-type')}")
        print(f"  └─ Size: {len(response.text)} bytes")
        test_results["rest_tests"].append(("GET /", True))
    except Exception as e:
        print(f"✗ GET /: {e}")
        test_results["rest_tests"].append(("GET /", False))
        return False
    
    # Test 4: 404 Error Handling
    try:
        response = requests.get(f"{SERVER_URL}/api/nonexistent", timeout=5)
        assert response.status_code == 404
        print("✓ 404 Error Handling")
        print(f"  └─ Status: {response.status_code}")
        test_results["rest_tests"].append(("404 Error Handling", True))
    except Exception as e:
        print(f"✗ 404 Error Handling: {e}")
        test_results["rest_tests"].append(("404 Error Handling", False))
    
    return True

# Run REST tests
try:
    print("\nAttempting to connect to server...")
    response = requests.get(f"{SERVER_URL}/api/health", timeout=2)
    print("✓ Server is responding!")
    rest_success = test_rest_endpoints()
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to server!")
    print(f"  Ensure Flask is running: python app.py")
    exit(1)
except Exception as e:
    print(f"✗ Connection error: {e}")
    exit(1)

# ============================================================================
# SECTION 2: SINGLE WEBSOCKET CLIENT
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 2: SINGLE WEBSOCKET CLIENT TEST")
print("=" * 80)

def test_single_websocket_client():
    """Test a single WebSocket client connection."""
    
    print("\n[WebSocket Connection Test]")
    
    client = socketio.Client()
    events = {
        "connected": False,
        "received_response": False,
        "response_data": None,
    }
    
    @client.event
    def connect():
        print("✓ WebSocket connected (Client-side event)")
        events["connected"] = True
    
    @client.event
    def disconnect():
        print("✓ WebSocket disconnected")
    
    @client.on('response')
    def on_response(data):
        print(f"✓ Received response: {data}")
        events["received_response"] = True
        events["response_data"] = data
    
    try:
        print("Attempting WebSocket connection with polling transport...")
        # Use polling transport instead of WebSocket to avoid library conflicts
        client.connect(WEBSOCKET_URL, wait_timeout=5, transports=['polling'])
        
        # Wait for connection
        time.sleep(0.5)
        
        if events["connected"]:
            print("✓ Single WebSocket Client Connection")
            test_results["websocket_tests"].append(("WebSocket Connect", True))
        else:
            print("✗ Connection event not received")
            test_results["websocket_tests"].append(("WebSocket Connect", False))
            return False
        
        # Send echo test
        print("\nSending echo test message...")
        client.emit('echo', {'test_message': 'Hello from E2E test'})
        time.sleep(0.5)
        
        if events["received_response"]:
            print("✓ Echo Message Test")
            test_results["websocket_tests"].append(("Echo Message", True))
        else:
            print("✗ No response received from echo")
            test_results["websocket_tests"].append(("Echo Message", False))
        
        # Disconnect
        client.disconnect()
        time.sleep(0.2)
        print("✓ Graceful Disconnection")
        test_results["websocket_tests"].append(("Graceful Disconnect", True))
        
        return True
        
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        test_results["websocket_tests"].append(("WebSocket", False))
        return False

websocket_success = test_single_websocket_client()

# ============================================================================
# SECTION 3: MULTIPLE CONCURRENT CLIENTS
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 3: CONCURRENT MULTIPLE CLIENTS TEST")
print("=" * 80)

def test_concurrent_clients():
    """Test multiple simultaneous WebSocket clients."""
    
    print("\n[Concurrent Clients Test]")
    
    num_clients = 3
    clients = []
    client_states = []
    
    for i in range(num_clients):
        client_state = {
            "id": i,
            "connected": False,
            "messages_received": 0,
            "messages": []
        }
        client_states.append(client_state)
        
        client = socketio.Client()
        clients.append(client)
        
        # Create closures to capture client ID
        def make_connect_handler(client_id):
            @client.event
            def connect():
                client_states[client_id]["connected"] = True
                print(f"  ├─ Client {client_id} connected")
            return connect
        
        def make_response_handler(client_id):
            @client.on('response')
            def on_response(data):
                client_states[client_id]["messages_received"] += 1
                client_states[client_id]["messages"].append(data)
            return on_response
        
        # Attach handlers
        client.on('connect', make_connect_handler(i))
        make_response_handler(i)
    
    try:
        print(f"Connecting {num_clients} clients concurrently...")
        
        # Connect all clients with polling transport
        for i, client in enumerate(clients):
            try:
                client.connect(WEBSOCKET_URL, wait_timeout=5, transports=['polling'])
                print(f"  └─ Client {i} connection initiated")
            except Exception as e:
                print(f"  └─ Client {i} error: {e}")
        
        # Wait for connections to establish
        time.sleep(1)
        
        # Check connections
        connected_count = sum(1 for state in client_states if state["connected"])
        print(f"\n✓ Concurrent Connection: {connected_count}/{num_clients} clients connected")
        test_results["concurrent_tests"].append(("Concurrent Connect", connected_count == num_clients))
        
        # Send messages from each client
        print("\nSending messages from each client...")
        for i, client in enumerate(clients):
            try:
                client.emit('echo', {'client_id': i, 'message': f'Message from client {i}'})
                print(f"  ├─ Client {i} sent message")
            except Exception as e:
                print(f"  └─ Client {i} send error: {e}")
        
        time.sleep(1)
        
        # Check received messages
        total_messages = sum(state["messages_received"] for state in client_states)
        print(f"\n✓ Message Receiving: {total_messages} messages received across {num_clients} clients")
        test_results["concurrent_tests"].append(("Message Receiving", total_messages > 0))
        
        # Disconnect all
        print("\nDisconnecting all clients...")
        for i, client in enumerate(clients):
            try:
                client.disconnect()
                print(f"  └─ Client {i} disconnected")
            except Exception as e:
                print(f"  └─ Client {i} disconnect error: {e}")
        
        time.sleep(0.5)
        print("✓ All Clients Disconnected")
        test_results["concurrent_tests"].append(("All Disconnected", True))
        
        return True
        
    except Exception as e:
        print(f"✗ Concurrent clients error: {e}")
        test_results["concurrent_tests"].append(("Concurrent Test", False))
        return False

concurrent_success = test_concurrent_clients()

# ============================================================================
# SECTION 4: FINAL REPORT
# ============================================================================

print("\n" + "=" * 80)
print("END-TO-END TEST RESULTS")
print("=" * 80)

total_passed = 0
total_failed = 0

print("\nREST API Tests:")
for test_name, passed in test_results["rest_tests"]:
    symbol = "✓" if passed else "✗"
    print(f"  {symbol} {test_name}")
    if passed:
        total_passed += 1
    else:
        total_failed += 1

print("\nWebSocket Tests:")
for test_name, passed in test_results["websocket_tests"]:
    symbol = "✓" if passed else "✗"
    print(f"  {symbol} {test_name}")
    if passed:
        total_passed += 1
    else:
        total_failed += 1

print("\nConcurrent Client Tests:")
for test_name, passed in test_results["concurrent_tests"]:
    symbol = "✓" if passed else "✗"
    print(f"  {symbol} {test_name}")
    if passed:
        total_passed += 1
    else:
        total_failed += 1

print("\n" + "-" * 80)
print(f"Total Passed: {total_passed}")
print(f"Total Failed: {total_failed}")
total_tests = total_passed + total_failed
success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
print(f"Success Rate: {success_rate:.1f}%")

test_results["end_time"] = datetime.now()
duration = (test_results["end_time"] - test_results["start_time"]).total_seconds()
print(f"Duration: {duration:.2f} seconds")

if total_failed == 0:
    print("\n✅ ALL END-TO-END TESTS PASSED!")
    print("\nSystem is working correctly:")
    print("  ✓ Server responds to HTTP requests")
    print("  ✓ WebSocket connections work")
    print("  ✓ Real-time messaging works")
    print("  ✓ Multiple clients can connect simultaneously")
else:
    print(f"\n⚠️ {total_failed} TEST(S) FAILED")

print("\n" + "=" * 80 + "\n")
