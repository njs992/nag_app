# End-to-End Testing Plan

## Overview

Full system testing with:
1. **Flask server running** (real process)
2. **Real network connections** (HTTP + WebSocket)
3. **Multiple concurrent clients**
4. **Full data flow verification**

---

## Test Phases

### Phase 1: Server Startup
- [ ] Start Flask server on localhost:5000
- [ ] Verify server accepts connections
- [ ] Health check endpoint responds

### Phase 2: REST API Testing
- [ ] GET /api/health
- [ ] GET /api/config
- [ ] GET / (static files)
- [ ] Response times acceptable
- [ ] Proper HTTP status codes

### Phase 3: Single WebSocket Client
- [ ] Client connects successfully
- [ ] Server receives connection event
- [ ] Client receives response
- [ ] Echo test works
- [ ] Client disconnects cleanly

### Phase 4: Multiple Concurrent Clients
- [ ] 3 clients connect simultaneously
- [ ] All receive connection confirmation
- [ ] Each can send independent messages
- [ ] Messages don't cross between clients
- [ ] All disconnect cleanly

### Phase 5: Data Persistence Integration
- [ ] Save character via REST call
- [ ] WebSocket client receives update event
- [ ] Load character and verify data
- [ ] Multiple clients see same data

### Phase 6: Stress Testing
- [ ] Rapid message sends
- [ ] Large message handling
- [ ] Connection/reconnection
- [ ] Server stability

---

## Success Criteria

✅ Server starts without errors  
✅ All REST endpoints respond with HTTP 200  
✅ WebSocket connections establish  
✅ Messages flow both directions  
✅ Multiple clients work simultaneously  
✅ Data persists correctly  
✅ No crashes or unhandled exceptions  
✅ Response times < 100ms  

---

## Test Environment

- **Host**: 127.0.0.1
- **Port**: 5000
- **Clients**: Python socketio client library
- **Duration**: ~5 minutes

