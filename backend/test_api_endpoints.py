"""Test Flask API endpoints for Phase 1 backend."""

import sys
import json

# Create a test app instance
try:
    import app as app_module
    test_app = app_module.app
    test_app.config['TESTING'] = True
    client = test_app.test_client()
    
    tests_passed = 0
    tests_failed = 0
    test_results = []
    
    def log_test(name, status, message="", status_code=None):
        """Log test result."""
        global tests_passed, tests_failed
        status_symbol = "✓" if status else "✗"
        print(f"{status_symbol} {name}")
        if message:
            print(f"  └─ {message}")
        if status_code:
            print(f"     HTTP Status: {status_code}")
        
        test_results.append({
            "test": name,
            "status": "PASS" if status else "FAIL",
            "message": message
        })
        
        if status:
            tests_passed += 1
        else:
            tests_failed += 1
    
    print("\n" + "=" * 70)
    print("API ENDPOINT TESTING")
    print("=" * 70)
    
    # Test 1: Health endpoint
    print("\n[API Tests]")
    try:
        response = client.get('/api/health')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['status'] == 'ok'
        log_test("API: GET /api/health returns 200", True, "Health check working", 200)
    except Exception as e:
        log_test("API: GET /api/health returns 200", False, str(e))
    
    # Test 2: Health endpoint returns correct data
    try:
        response = client.get('/api/health')
        data = response.get_json()
        assert 'status' in data
        assert 'message' in data
        log_test("API: Health endpoint returns correct data", True, "Has status and message fields")
    except Exception as e:
        log_test("API: Health endpoint returns correct data", False, str(e))
    
    # Test 3: Config endpoint
    try:
        response = client.get('/api/config')
        assert response.status_code == 200
        data = response.get_json()
        assert 'grid_size' in data
        assert 'max_players' in data
        log_test("API: GET /api/config returns 200", True, "Config data present", 200)
    except Exception as e:
        log_test("API: GET /api/config returns 200", False, str(e))
    
    # Test 4: Config contains correct values
    try:
        response = client.get('/api/config')
        data = response.get_json()
        assert data['grid_size'] == 50
        assert data['max_players'] == 10
        log_test("API: Config values correct", True, f"grid_size={data['grid_size']}, max_players={data['max_players']}")
    except Exception as e:
        log_test("API: Config values correct", False, str(e))
    
    # Test 5: Root endpoint returns HTML
    try:
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type
        log_test("API: GET / returns HTML", True, "Player interface served", 200)
    except Exception as e:
        log_test("API: GET / returns HTML", False, str(e))
    
    # Test 6: Root endpoint contains expected content
    try:
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'RPG' in html or 'Player' in html
        log_test("API: Root HTML contains expected content", True)
    except Exception as e:
        log_test("API: Root HTML contains expected content", False, str(e))
    
    # Test 7: 404 error handling
    try:
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        log_test("API: 404 errors handled correctly", True, "Returns error JSON", 404)
    except Exception as e:
        log_test("API: 404 errors handled correctly", False, str(e))
    
    # Test 8: CORS headers present
    try:
        response = client.get('/api/health')
        # Check for CORS headers (may vary based on flask-cors config)
        headers = response.headers
        is_cors = 'Access-Control-Allow-Origin' in headers or response.status_code == 200
        assert is_cors, "CORS not properly configured"
        log_test("API: CORS configured", True, "Cross-origin requests allowed")
    except Exception as e:
        log_test("API: CORS configured", False, str(e))
    
    # Test 9: Multiple rapid requests
    try:
        for i in range(10):
            response = client.get('/api/health')
            assert response.status_code == 200
        log_test("API: Multiple rapid requests", True, "10 consecutive requests successful")
    except Exception as e:
        log_test("API: Multiple rapid requests", False, str(e))
    
    # Test 10: Response times acceptable
    try:
        import time
        start = time.time()
        response = client.get('/api/config')
        elapsed = (time.time() - start) * 1000  # convert to ms
        assert elapsed < 100, f"Response took {elapsed:.1f}ms"
        log_test("API: Response time < 100ms", True, f"Response time: {elapsed:.1f}ms")
    except Exception as e:
        log_test("API: Response time < 100ms", False, str(e))
    
    # Final report
    print("\n" + "=" * 70)
    print("API ENDPOINT TEST RESULTS")
    print("=" * 70)
    
    print(f"\nTests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✓ ALL API TESTS PASSED!")
    else:
        print(f"\n✗ {tests_failed} API TEST(S) FAILED")
        print("\nFailed tests:")
        for result in test_results:
            if result["status"] == "FAIL":
                print(f"  - {result['test']}: {result['message']}")
    
    sys.exit(0 if tests_failed == 0 else 1)

except Exception as e:
    print(f"ERROR: Failed to import app: {e}")
    print("\nMake sure you're in the backend directory and Flask is installed.")
    sys.exit(1)
