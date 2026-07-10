import urllib.request
import json
import sys

BASE_URL = 'http://localhost:3000'

def test_endpoint(name, path, method='GET', data=None):
    url = f"{BASE_URL}{path}"
    print(f"Testing {name} [{method}] on {url}...")
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            jsondata = json.dumps(data).encode('utf-8')
            response = urllib.request.urlopen(req, data=jsondata, timeout=5)
        else:
            response = urllib.request.urlopen(req, timeout=5)
            
        res_data = json.loads(response.read().decode('utf-8'))
        if res_data.get('success'):
            print(f"[PASS] {name} Success!")
            return res_data
        else:
            print(f"[FAIL] {name} Failed: success=False. Response: {res_data}")
            return None
    except Exception as e:
        print(f"[ERROR] {name} Error: {e}")
        return None

def main():
    print("=== STARTING STADIUM OPS API TESTS ===")
    
    # 1. Test Dashboard stats
    dash = test_endpoint("Dashboard Telemetry", "/api/dashboard")
    if not dash:
        sys.exit(1)
        
    # 2. Test Concessions List
    test_endpoint("Concessions Telemetry", "/api/concessions")
    
    # 3. Test Zones List
    test_endpoint("Crowd Zones Telemetry", "/api/zones")
    
    # 4. Test Incidents Fetch
    test_endpoint("Incidents Telemetry", "/api/incidents")
    
    # 5. Test Live Simulation
    test_endpoint("Simulation Trigger", "/api/zones/simulate", method='POST')
    
    # 6. Test Sustainability Action Logging
    test_endpoint("Sustainability Logger", "/api/sustainability", method='POST', data={
        "username": "TestFan42",
        "action_type": "Recycled Plastic Bottle"
    })
    
    # 7. Test Sustainability Leaderboard
    test_endpoint("Leaderboard", "/api/sustainability/leaderboard")
    
    # 8. Test AI Assistant Chat
    test_endpoint("AI Fan Assistant Chat", "/api/ai/chat", method='POST', data={
        "message": "How do I get to Gate 1?"
    })
    
    # 9. Test Incident Dispatcher Parser
    test_endpoint("GenAI Incident Dispatcher", "/api/incidents/report", method='POST', data={
        "location": "Sector A Level 1 near concessions",
        "description": "Spilled large soda on floor, creating slip risk."
    })
    
    # 10. Test Command Center CLI
    test_endpoint("AI Command Center Intelligence", "/api/ai/command", method='POST', data={
        "command": "List active security alerts"
    })
    
    print("=== ALL STADIUM OPS API TESTS COMPLETED ===")

if __name__ == '__main__':
    main()
