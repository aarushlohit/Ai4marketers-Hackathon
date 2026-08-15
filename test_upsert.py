import requests
import json

url = "https://mb-backend-rnhn.onrender.com/api/v1/internal/customers/upsert"
payload = {
    "tenant_id": "8b28f488-2c65-46f9-82fa-e9d5e321cae4",
    "external_id": "test1234",
    "crm_source": "hubspot",
    "first_name": "Test",
    "last_name": "User"
}
headers = {"Content-Type": "application/json"}
res = requests.post(url, json=payload, headers=headers)
print("Status:", res.status_code)
print("Body:", res.text)
