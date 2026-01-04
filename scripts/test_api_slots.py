import json
import urllib.request
import urllib.error
import datetime

# Configuration
BASE_URL = "http://localhost:8069"
HEADERS = {'Content-Type': 'application/json'}

def test_slots():
    print("Testing /appointment/json/slots...")
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    payload = {
        "jsonrpc": "2.0", 
        "method": "call", 
        "params": {
            "employee_id": 1, 
            "service_product_id": 1, 
            "date_str": "2026-01-05" # Future date
        }
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/appointment/json/slots", data=data, headers=HEADERS)
    
    try:
        with urllib.request.urlopen(req) as response:
            status = response.getcode()
            body = response.read().decode('utf-8')
            
            print(f"Status: {status}")
            print("Response:", body[:500])
            
            if status == 200 and "slots" in body:
                print("✅ API Test Passed: Slots returned.")
            else:
                print("❌ API Test Failed or No Slots.")
                
    except urllib.error.URLError as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_slots()
