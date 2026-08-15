"""Local mock CRM provider for OAuth and CRM API demos.

This service emulates enough of Zoho CRM and Salesforce to validate the
connector flow without third-party accounts.
"""

import os
from urllib.parse import urlencode

from fastapi import FastAPI, Form, Query
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="Miracle Birds Mock CRM Provider",
    description="Local OAuth and CRM API emulator for Zoho CRM and Salesforce",
    version="1.0.0",
)

INTERNAL_BASE_URL = os.getenv("MOCK_CRM_INTERNAL_BASE_URL", "http://mock_crm_provider:8900").rstrip("/")


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "healthy", "service": "mock-crm-provider"}


@app.get("/oauth/{crm_type}/authorize")
async def authorize(
    crm_type: str,
    redirect_uri: str = Query(...),
    state: str = Query(...),
):
    """Auto-approve local OAuth and redirect back with a fake code."""
    params = urlencode({"code": f"mock-{crm_type}-code", "state": state})
    separator = "&" if "?" in redirect_uri else "?"
    return RedirectResponse(f"{redirect_uri}{separator}{params}", status_code=302)


@app.post("/oauth/{crm_type}/token")
async def token(
    crm_type: str,
    grant_type: str = Form(...),
    code: str | None = Form(default=None),
    refresh_token: str | None = Form(default=None),
):
    """Return deterministic mock OAuth tokens."""
    access_token = f"mock-{crm_type}-access-token"
    response = {
        "access_token": access_token,
        "refresh_token": refresh_token or f"mock-{crm_type}-refresh-token",
        "expires_in": 3600,
        "token_type": "Bearer",
        "scope": "mock.crm.full",
    }
    if crm_type == "salesforce":
        response["instance_url"] = INTERNAL_BASE_URL
    elif crm_type == "zoho":
        response["api_domain"] = INTERNAL_BASE_URL
    return response


@app.get("/services/oauth2/userinfo")
async def salesforce_userinfo():
    return {
        "user_id": "mock-salesforce-user",
        "organization_id": "mock-salesforce-org",
        "preferred_username": "sales@example.com",
    }


@app.get("/services/data/v58.0/query")
async def salesforce_query(q: str = Query(default="")):
    records = [
        {
            "Id": "SF-CON-001",
            "FirstName": "Avery",
            "LastName": "Stone",
            "Email": "avery.stone@example.com",
            "Phone": "+1-415-555-0130",
            "Title": "VP Marketing",
            "Account": {"Name": "Northstar Analytics"},
        },
        {
            "Id": "SF-CON-002",
            "FirstName": "Mina",
            "LastName": "Patel",
            "Email": "mina.patel@example.com",
            "Phone": "+1-212-555-0188",
            "Title": "Revenue Operations Lead",
            "Account": {"Name": "Atlas Retail"},
        },
    ]
    return {"totalSize": len(records), "done": True, "records": records}


@app.get("/crm/v3/users")
async def zoho_current_user(type: str = Query(default="CurrentUser")):
    return {
        "users": [
            {
                "id": "mock-zoho-user",
                "full_name": "Zoho Demo User",
                "email": "zoho@example.com",
            }
        ]
    }


@app.get("/crm/v3/Contacts")
async def zoho_contacts(per_page: int = Query(default=100), page: int = Query(default=1)):
    return {
        "data": [
            {
                "id": "ZOHO-CON-001",
                "First_Name": "Nora",
                "Last_Name": "Iyer",
                "Email": "nora.iyer@example.com",
                "Phone": "+91-98765-43210",
                "Title": "Growth Manager",
                "Account_Name": {"name": "Pavazhamalli Labs"},
            },
            {
                "id": "ZOHO-CON-002",
                "First_Name": "Leo",
                "Last_Name": "Martins",
                "Email": "leo.martins@example.com",
                "Phone": "+44-20-5555-0142",
                "Title": "CRM Administrator",
                "Account_Name": {"name": "Blue Finch Media"},
            },
        ],
        "info": {"per_page": per_page, "page": page, "more_records": False},
    }


@app.get("/crm/v3/Accounts")
async def zoho_accounts(per_page: int = Query(default=100)):
    return {
        "data": [
            {"id": "ZOHO-ACC-001", "Account_Name": "Pavazhamalli Labs"},
            {"id": "ZOHO-ACC-002", "Account_Name": "Blue Finch Media"},
        ],
        "info": {"per_page": per_page, "more_records": False},
    }


@app.get("/crm/v3/objects/contacts")
async def hubspot_contacts(limit: int = Query(default=100), after: int | None = Query(default=None)):
    """Deterministic HubSpot-shaped contact data for local connector tests."""
    records = [
        {
            "id": "HS-CON-001",
            "properties": {
                "firstname": "Isha",
                "lastname": "Menon",
                "email": "isha.menon@example.com",
                "phone": "+91-90000-10001",
                "company": "Northstar Analytics",
                "jobtitle": "Marketing Director",
            },
        },
        {
            "id": "HS-CON-002",
            "properties": {
                "firstname": "Daniel",
                "lastname": "Cole",
                "email": "daniel.cole@example.com",
                "phone": "+1-415-555-0199",
                "company": "Atlas Retail",
                "jobtitle": "RevOps Manager",
            },
        },
    ]
    return {"results": records[: min(limit, 100)], "paging": {}}


@app.get("/crm/v3/objects/companies")
async def hubspot_companies(limit: int = Query(default=100)):
    return {
        "results": [
            {"id": "HS-COMP-001", "properties": {"name": "Northstar Analytics"}},
            {"id": "HS-COMP-002", "properties": {"name": "Atlas Retail"}},
        ][: min(limit, 100)],
    }
