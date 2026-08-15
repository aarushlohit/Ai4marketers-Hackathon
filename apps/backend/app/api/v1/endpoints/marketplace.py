"""Endpoints for Plugin & Agent Marketplace and Developer SDK guidelines."""

from typing import Annotated, List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.api.dependencies import CurrentUser, get_current_user, get_db

router = APIRouter()

class PluginInstallRequest(BaseModel):
    plugin_id: UUID
    settings: Dict[str, Any] = {}

class InstalledPluginResponse(BaseModel):
    id: UUID
    plugin_id: UUID
    name: str
    slug: str
    item_type: str
    description: str
    developer: str
    settings: Dict[str, Any]
    installed_at: str

@router.get("/plugins")
async def list_available_plugins(
    db: AsyncSession = Depends(get_db)
):
    """List all available marketplace plugins and agents."""
    try:
        res = await db.execute(
            "SELECT id, name, slug, item_type, description, developer, price, is_active FROM core.marketplace_items WHERE is_active = true"
        )
        rows = res.fetchall()
        plugins = []
        for r in rows:
            plugins.append({
                "id": r[0],
                "name": r[1],
                "slug": r[2],
                "item_type": r[3],
                "description": r[4],
                "developer": r[5],
                "price": r[6]
            })
        return plugins
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/installed", response_model=List[InstalledPluginResponse])
async def list_installed_plugins(
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all plugins installed for the tenant."""
    try:
        # PostgreSQL tenant context is set in get_db
        res = await db.execute(
            """
            SELECT i.id, i.plugin_id, m.name, m.slug, m.item_type, m.description, m.developer, i.settings, i.installed_at
            FROM core.installed_plugins i
            JOIN core.marketplace_items m ON i.plugin_id = m.id
            WHERE i.tenant_id = :tenant_id
            """,
            {"tenant_id": user.tenant_id}
        )
        rows = res.fetchall()
        installed = []
        for r in rows:
            installed.append(InstalledPluginResponse(
                id=r[0],
                plugin_id=r[1],
                name=r[2],
                slug=r[3],
                item_type=r[4],
                description=r[5],
                developer=r[6],
                settings=r[7] if isinstance(r[7], dict) else json.loads(r[7] or "{}"),
                installed_at=r[8].isoformat() if hasattr(r[8], "isoformat") else str(r[8])
            ))
        return installed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/install", status_code=201)
async def install_plugin(
    payload: PluginInstallRequest,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Install a plugin for the tenant."""
    try:
        # Check if already installed
        dup = await db.execute(
            "SELECT id FROM core.installed_plugins WHERE tenant_id = :tid AND plugin_id = :pid",
            {"tid": user.tenant_id, "pid": payload.plugin_id}
        )
        if dup.fetchone():
            raise HTTPException(status_code=400, detail="Plugin is already installed.")

        # Verify plugin exists
        exists = await db.execute(
            "SELECT id FROM core.marketplace_items WHERE id = :id",
            {"id": payload.plugin_id}
        )
        if not exists.fetchone():
            raise HTTPException(status_code=404, detail="Marketplace plugin not found.")

        # Save installation
        await db.execute(
            """
            INSERT INTO core.installed_plugins (tenant_id, plugin_id, settings)
            VALUES (:tid, :pid, :settings)
            """,
            {
                "tid": user.tenant_id,
                "pid": payload.plugin_id,
                "settings": json.dumps(payload.settings)
            }
        )
        await db.commit()
        return {"status": "success", "message": "Plugin installed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/install/{plugin_id}")
async def uninstall_plugin(
    plugin_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Uninstall a plugin for the tenant."""
    try:
        res = await db.execute(
            "DELETE FROM core.installed_plugins WHERE tenant_id = :tid AND plugin_id = :pid",
            {"tid": user.tenant_id, "pid": plugin_id}
        )
        await db.commit()
        return {"status": "success", "message": "Plugin uninstalled successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sdk/docs", response_class=PlainTextResponse)
async def get_sdk_docs():
    """Retrieve developer guidelines and boilerplate code for the SDK."""
    sdk_text = """
========================================================================
                      🐦 MIRACLE BIRDS DEVELOPER SDK
========================================================================

Miracle Birds allows third-party developers to extend CRM intelligence 
capabilities using Custom AI Agents, Automation Plugins, and Connectors.

------------------------------------------------------------------------
GETTING STARTED:

All extensions must implement the standard Miracle Birds plugin format.
An automation plugin receives workflow payloads and executes custom jobs.

------------------------------------------------------------------------
PYTHON EXTENSION TEMPLATE:

```python
# Save as custom_plugin.py
from typing import Dict, Any

class MiracleBirdsPlugin:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.api_key = settings.get("api_key")

    async def execute(self, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Execute the custom extension step.
        \"\"\"
        if action_type == "enrich_lead":
            # Call external services to gather business data
            company = payload.get("company", "Unknown")
            enriched_data = {
                "linkedin_url": f"https://linkedin.com/company/{company.lower()}",
                "employee_count": 250,
                "source": "EnrichmentExtension"
            }
            return {
                "status": "success",
                "output": enriched_data,
                "rollback_step": "retract_enrichment"
            }
        return {"status": "skipped", "message": "Action not supported"}

    async def rollback(self, action_type: str, rollback_data: Dict[str, Any]):
        \"\"\"
        Reverse side-effects if subsequent workflow steps fail.
        \"\"\"
        print("Rolling back custom action:", action_type)
```

------------------------------------------------------------------------
AGENT UPGRADE FORMAT:

If you are developing a Custom Agent, implement the system prompt and 
expose a list of LangChain tools. Example config:

```json
{
  "name": "Custom Marketing Copywriter Agent",
  "agent_type": "marketing",
  "system_prompt": "You are a copywriter that generates high-converting emails based on lead score dynamics.",
  "tools": [
    {"name": "generate_copy", "description": "Generates custom copy layouts"}
  ],
  "permissions": {
    "can_access_customers": true,
    "can_send_communications": true
  }
}
```

------------------------------------------------------------------------
SUPPORT & SUBMISSIONS:
Submit your compiled zip plugin archive to developer@miraclebirds.com.
========================================================================
"""
    return sdk_text
