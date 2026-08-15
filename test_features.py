import urllib.request
import json

services = {
    "Backend API": 18000,
    "AI Engine": 28001,
    "ML Engine": 28002,
    "CRM Integration": 28003,
    "Security Engine": 28004,
    "Workflow Engine": 28005,
    "Agent Service": 28101,
    "Memory Service": 28102,
    "Knowledge Service": 28103,
    "Search Service": 28104,
    "Reasoning Service": 28105,
    "Simulation Service": 28106,
    "Executive Service": 28107,
    "Customer Twin Service": 28108,
    "Observability Service": 28109,
}

all_good = True
for name, port in services.items():
    try:
        url = f"http://localhost:{port}/health"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"✅ {name} (Port {port}) is ONLINE")
            else:
                print(f"❌ {name} (Port {port}) returned status {response.status}")
                all_good = False
    except Exception as e:
        print(f"❌ {name} (Port {port}) FAILED: {str(e)}")
        all_good = False

print("\nResult:", "ALL SYSTEMS GO 🚀" if all_good else "SOME SYSTEMS OFFLINE ⚠️")
