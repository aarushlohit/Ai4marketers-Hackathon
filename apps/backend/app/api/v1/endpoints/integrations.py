"""CRM integration endpoints: OAuth flow, connections, sync management."""

from typing import Annotated, Literal
from uuid import UUID

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import CurrentUser, get_current_user
from app.core.config import settings

logger = structlog.get_logger()

router = APIRouter()

CRM_SERVICE_URL = getattr(settings, "CRM_SERVICE_URL", "http://crm_integration:8003")

CRMType = Literal["salesforce", "zoho", "hubspot", "dynamics", "pipedrive", "frappe"]


async def _crm_request(method: str, path: str, **kwargs) -> dict:
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.request(method, f"{CRM_SERVICE_URL}{path}", **kwargs)
            r.raise_for_status()
            return r.json() if r.content else {}
        except httpx.HTTPStatusError as e:
            logger.error("crm_service_status_error", url=str(e.request.url), status_code=e.response.status_code, text=e.response.text[:500])
            err_msg = str(e.response.status_code)
            try:
                err_body = e.response.json()
                if "detail" in err_body:
                    err_msg = str(err_body["detail"])
            except Exception:
                if e.response.text:
                    err_msg = f"{e.response.status_code} ({e.response.text[:200].strip()})"
            raise HTTPException(status.HTTP_502_BAD_GATEWAY,
                                detail=f"CRM service error: {err_msg}")
        except httpx.RequestError as e:
            logger.error("crm_service_request_error", error=str(e))
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                                detail=f"CRM Integration service unavailable: {str(e)}")


@router.get("/{crm_type}/authorize")
async def initiate_oauth(
    crm_type: CRMType,
    request: Request,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    redirect_uri: str | None = Query(default=None),
):
    """Generate the OAuth authorization URL for the given CRM."""
    callback_url = redirect_uri or str(
        request.url_for("crm_oauth_callback", crm_type=crm_type)
    )
    result = await _crm_request(
        "GET",
        f"/{crm_type}/authorize",
        params={"tenant_id": str(user.tenant_id), "redirect_uri": callback_url},
    )
    return result


@router.get("/{crm_type}/callback", name="crm_oauth_callback")
async def oauth_callback(
    crm_type: CRMType,
    code: str = Query(...),
    state: str = Query(...),
    redirect_uri: str | None = Query(default=None),
):
    """Proxy OAuth callbacks from CRM providers into the CRM Integration service."""
    params = {"code": code, "state": state}
    if redirect_uri:
        params["redirect_uri"] = redirect_uri

    result = await _crm_request(
        "GET",
        f"/{crm_type}/callback",
        params=params,
    )
    
    frontend_url = settings.FRONTEND_URL.rstrip("/")
    return RedirectResponse(
        url=f"{frontend_url}/integrations?integration={crm_type}&status=connected",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/connections")
async def list_connections(user: Annotated[CurrentUser, Depends(get_current_user)]):
    """List all active CRM connections for the tenant."""
    return await _crm_request("GET", "/connections",
                              params={"tenant_id": str(user.tenant_id)})


@router.delete("/connections/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_connection(
    connection_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Disconnect and remove a CRM connection."""
    await _crm_request("DELETE", f"/connections/{connection_id}",
                       params={"tenant_id": str(user.tenant_id)})

@router.delete("/connections", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_connections(user: Annotated[CurrentUser, Depends(get_current_user)]):
    """Remove every CRM connection owned by the current tenant."""
    await _crm_request("DELETE", "/connections", params={"tenant_id": str(user.tenant_id)})


@router.post("/sync/{connection_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def start_sync(
    connection_id: UUID,
    user: Annotated[CurrentUser, Depends(get_current_user)],
    sync_type: Literal["full", "incremental"] = Query(default="incremental"),
):
    """Manually trigger a CRM data sync job."""
    return await _crm_request("POST", f"/sync/{connection_id}/start",
                              params={"sync_type": sync_type,
                                      "tenant_id": str(user.tenant_id)})


@router.get("/sync/{job_id}/status")
async def get_sync_status(
    job_id: str,
    user: Annotated[CurrentUser, Depends(get_current_user)],
):
    """Check the status of a running sync job."""
    return await _crm_request("GET", f"/sync/{job_id}/status")
